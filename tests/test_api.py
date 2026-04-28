import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock

client = TestClient(app)

def test_generate_certificate_flow(mocker):
    # Mock de GoogleDriveService
    mock_drive = mocker.patch("app.api.routes.GoogleDriveService")
    mock_drive_instance = mock_drive.return_value
    mock_drive_instance.upload_pdf.return_value = "https://drive.google.com/test-pdf-link"

    # Mock de BigQueryService
    mock_bq = mocker.patch("app.api.routes.BigQueryService")
    mock_bq_instance = mock_bq.return_value
    mock_bq_instance.log_policy.return_value = None

    # Payload de prueba
    payload = {
        "nombre_beneficiario": "Carlos Prueba",
        "numero_credito": "CRED-12345",
        "cuv": "ABCDEF1234567890",
        "poliza": "POL-TEST-001",
        "direccion_vivienda": {
            "domicilio": "Av. Reforma 222",
            "colonia": "Juarez",
            "codigo_postal": "06600",
            "municipio": "Cuauhtemoc",
            "estado": "CDMX"
        },
        "numero_certificado": "CERT-889900",
        "nombre_asegurado": "Juan Asegurado",
        "valor_avaluo": 2500000.0,
        "coberturas_vigencias": {
            "Estructura (10 años)": {"desde": "2024-01-01", "hasta": "2034-01-01"},
            "Impermeabilización (5 años)": {"desde": "2024-01-01", "hasta": "2029-01-01"},
            "Instalaciones (2 años)": {"desde": "2024-01-01", "hasta": "2026-01-01"}
        },
        "sello_digital": "SELLO-DIGITAL-DE-PRUEBA-1234567890"
    }

    # Ejecutar la petición
    response = client.post("/generate-certificate", json=payload)

    # Validaciones
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["url_descarga_pdf"] == "https://drive.google.com/test-pdf-link"
    
    # Verificar que se llamaron a los servicios
    mock_drive_instance.upload_pdf.assert_called_once()
    mock_bq_instance.log_policy.assert_called_once()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
