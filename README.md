# Vivienda API - Senior SecOps Backend

API RESTful para la gestión automatizada de certificados de póliza de vivienda.

## Características
- **FastAPI:** Documentación interactiva (Swagger/Redoc).
- **ReportLab:** Generación de PDF en memoria.
- **GDrive API:** Organización automática de carpetas por Póliza/Certificado.
- **BigQuery:** Registro histórico de transacciones.
- **Seguridad:** Validación estricta con Pydantic y ejecución en contenedor no-root.

## Requisitos Previos
- Docker instalado.
- Cuenta de Servicio de Google Cloud con permisos para:
  - Google Drive API (acceso a archivos y carpetas).
  - Google BigQuery (inserción de datos).
- La Cuenta de Servicio debe estar habilitada en el proyecto de GCP.

## Configuración y Ejecución

### 1. Variables de Entorno
El sistema requiere las credenciales de Google en formato JSON pasadas como un string.

### 2. Construir la Imagen
```bash
docker build -t viviendapi .
```

### 3. Ejecutar el Contenedor
Reemplaza el contenido de `GOOGLE_CREDENTIALS_JSON` con el JSON de tu cuenta de servicio (puedes usar `cat key.json | tr -d '\n'`).

```bash
docker run -p 8000:8000 \
  -e GOOGLE_CREDENTIALS_JSON='{ "type": "service_account", ... }' \
  -e BQ_DATASET='sinestry_infonavit' \
  -e BQ_TABLE='polizas_vivienda' \
  viviendapi
```

## Documentación API
Una vez iniciado, accede a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Despliegue en Google Cloud (Cloud Run)

### 1. Configuración de Artifact Registry
```bash
gcloud artifacts repositories create vivienda-repo --repository-format=docker --location=us-central1
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 2. Build y Push
```bash
docker build -t us-central1-docker.pkg.dev/jkdemo001/vivienda-repo/viviendapi:v1 .
docker push us-central1-docker.pkg.dev/jkdemo001/vivienda-repo/viviendapi:v1
```

### 3. Deploy
```bash
gcloud run deploy vivienda-service \
    --image us-central1-docker.pkg.dev/jkdemo001/vivienda-repo/viviendapi:v1 \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="BQ_DATASET=vivienda_infonavit,BQ_TABLE=polizas_vivienda,SHARED_DRIVE_ID=0APoMNV1l2yBHUk9PVA,MOCK_MODE=false"
```

## Seguridad (Pentesting Ready)
- **Sanitización:** Los inputs son limpiados de etiquetas HTML/Scripts.
- **Validación:** Regex estricto para CUV y Códigos Postales.
- **Zero Credentials:** No se guardan archivos de llaves en el repo.
- **Least Privilege:** El contenedor corre con un usuario sin privilegios.
