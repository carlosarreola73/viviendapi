from fastapi import APIRouter, HTTPException, Query
from app.schemas.poliza import PolizaPayload, PolizaResponse, PolizaListResponse, PolizaPadrePayload
import uuid
from app.services.pdf_generator import PDFGenerator
from app.services.google_drive import GoogleDriveService
from app.services.bigquery import BigQueryService
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generar-certificado", response_model=PolizaResponse)
async def generar_certificado(payload: PolizaPayload):
    try:
        # Modo Mock para pruebas sin credenciales reales
        if os.getenv("MOCK_MODE", "false").lower() == "true":
            logger.info("MOCK_MODE: Simulando flujo de QR")
            mock_links = {
                "view_link": f"https://drive.google.com/mock-view/{payload.numero_certificado}",
                "download_link": f"https://drive.google.com/mock-download/{payload.numero_certificado}"
            }
            PDFGenerator.generate_policy_pdf(payload, mock_links["view_link"])
            return PolizaResponse(
                data=payload, 
                url_visualizacion=mock_links["view_link"],
                url_descarga_directa=mock_links["download_link"]
            )

        logger.info("Step 1: Checking/Registering Poliza Padre")
        bq_service = BigQueryService()
        master_policy = bq_service.get_poliza_padre_by_name(payload.poliza)
        
        if not master_policy:
            logger.info(f"Poliza Padre {payload.poliza} not found. Registering automatically...")
            generated_uid = f"AUTO-{uuid.uuid4().hex[:8].upper()}"
            new_master_data = PolizaPadrePayload(
                poliza=payload.poliza,
                inicio_vigencia=payload.coberturas_vigencias.estructura_10_anios.desde,
                fin_vigencia=payload.coberturas_vigencias.estructura_10_anios.hasta
            )
            bq_service.log_poliza_padre(generated_uid, new_master_data)
        
        logger.info("Step 2: Creating placeholder in Google Drive to get URL")
        drive_service = GoogleDriveService()
        links = drive_service.create_placeholder(
            policy_number=payload.poliza,
            cert_number=payload.numero_certificado
        )

        logger.info(f"Step 3: Generating PDF with QR pointing to {links['view_link']}")
        pdf_buffer = PDFGenerator.generate_policy_pdf(payload, qr_url=links["view_link"])
        
        logger.info("Step 4: Uploading final PDF content to Google Drive")
        drive_service.update_file_content(links["id"], pdf_buffer)
        
        logger.info("Step 5: Logging data to BigQuery")
        bq_service.log_policy(payload, links["view_link"])
        
        return PolizaResponse(
            data=payload, 
            url_visualizacion=links["view_link"],
            url_descarga_directa=links["download_link"]
        )
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during certificate generation")

@router.get("/polizas", response_model=PolizaListResponse)
async def listar_polizas(limit: int = Query(100, ge=1, le=1000)):
    try:
        if os.getenv("MOCK_MODE", "false").lower() == "true":
            return PolizaListResponse(total=1, items=[{"test": "data"}])
        bq_service = BigQueryService()
        items = bq_service.list_policies(limit=limit)
        return PolizaListResponse(total=len(items), items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- ENDPOINTS PÓLIZA PADRE ---

@router.post("/poliza-padre")
async def register_poliza_padre(payload: PolizaPadrePayload):
    try:
        if os.getenv("MOCK_MODE", "false").lower() == "true":
            return {"status": "success", "message": "Póliza padre registrada (MOCK)"}
        generated_uid = f"PAD-{uuid.uuid4().hex[:8].upper()}"
        bq_service = BigQueryService()
        bq_service.log_poliza_padre(generated_uid, payload)
        return {"status": "success", "message": "Póliza padre registrada", "uid": generated_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/polizas-padre", response_model=PolizaListResponse)
async def list_polizas_padre(limit: int = Query(100, ge=1, le=1000)):
    try:
        bq_service = BigQueryService()
        items = bq_service.list_polizas_padre(limit=limit)
        return PolizaListResponse(total=len(items), items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/poliza-padre/{uid}")
async def get_poliza_padre(uid: str):
    bq_service = BigQueryService()
    policy = bq_service.get_poliza_padre(uid)
    if not policy:
        raise HTTPException(status_code=404, detail="Póliza padre no encontrada")
    return policy

@router.put("/poliza-padre/{uid}")
async def update_poliza_padre(uid: str, payload: PolizaPadrePayload):
    try:
        bq_service = BigQueryService()
        if not bq_service.get_poliza_padre(uid):
            raise HTTPException(status_code=404, detail="Póliza padre no encontrada")
        bq_service.update_poliza_padre(uid, payload)
        return {"status": "success", "message": "Póliza padre actualizada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/poliza-padre/{uid}")
async def delete_poliza_padre(uid: str):
    try:
        bq_service = BigQueryService()
        if not bq_service.get_poliza_padre(uid):
            raise HTTPException(status_code=404, detail="Póliza padre no encontrada")
        bq_service.delete_poliza_padre(uid)
        return {"status": "success", "message": "Póliza padre eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
