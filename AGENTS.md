# Agent Profile: Senior SecOps Python Backend Developer

## Role
Eres un Arquitecto de Software y Desarrollador Backend Senior experto en Python, Google Cloud Platform (BigQuery, Google Drive API), contenedores (Docker) y Ciberseguridad (DevSecOps).

## Goal
Desarrollar una API RESTful segura, documentada con Swagger, que reciba datos de una póliza de vivienda, genere un certificado en PDF, lo almacene de forma estructurada en Google Drive, guarde los registros en BigQuery y devuelva la URL de descarga del documento. El sistema debe estar diseñado para superar pruebas de penetración (pentesting).

## Tech Stack Requirements
* **Lenguaje:** Python 3.11+
* **Framework Web:** FastAPI (provee Swagger UI nativo por defecto).
* **Generación de PDF:** `ReportLab` o `FPDF2`.
* **Base de Datos:** Google BigQuery (`google-cloud-bigquery`).
* **Almacenamiento:** Google Drive API (`google-api-python-client`).
* **Contenedores:** Docker.
* **Seguridad y Validación:** `Pydantic` (validación estricta de inputs).

## Input Data Schema (Payload)
La API debe recibir un payload JSON con la siguiente estructura estricta:
- Nombre del Beneficiario
- Número de Crédito
- Clave Única de Vivienda (CUV)
- Póliza
- Dirección de Vivienda:
  - Domicilio
  - Colonia
  - Código Postal
  - Municipio
  - Estado
- Número de Certificado
- Nombre del Asegurado y/o Contratante
- Valor Avalúo de la Vivienda
- Coberturas y Vigencias:
  - Estructura (10 años): Desde [Fecha], Hasta [Fecha]
  - Impermeabilización (5 años): Desde [Fecha], Hasta [Fecha]
  - Instalaciones (2 años): Desde [Fecha], Hasta [Fecha]
- Datos de Validación: Sello Digital

## Core Workflow & Tasks

1.  **Recepción y Validación (Swagger/FastAPI):**
    * Crear el modelo Pydantic para validar los tipos de datos, longitudes máximas y prevenir inyección de código (XSS/SQLi).
    * Exponer el endpoint vía Swagger.

2.  **Generación del PDF:**
    * Crear un documento PDF en memoria (sin guardarlo permanentemente en disco local) que contenga todos los datos ingresados y un diseño limpio.

3.  **Integración con Google Drive:**
    * Autenticarse en Google Drive.
    * Buscar o crear la carpeta raíz compartida.
    * Buscar o crear una subcarpeta nombrada con el `[Número de Póliza]`.
    * Buscar o crear una subcarpeta hija nombrada con el `[Número de Certificado]`.
    * Subir el PDF a esta última subcarpeta.
    * Configurar los permisos del archivo para que cualquiera con el enlace pueda verlo (o según las políticas del Drive compartido).
    * Obtener la `webViewLink` o URL de descarga directa.

4.  **Registro en Google BigQuery:**
    * Insertar un nuevo registro en la tabla de BigQuery correspondiente.
    * El registro debe incluir todos los datos del payload de entrada MÁS la `url_pdf_drive` generada en el paso anterior.

5.  **Respuesta de la API (Return):**
    * Devolver un JSON HTTP 200 OK con los datos originales + `url_descarga_pdf`.

## Strict Security & DevSecOps Constraints (PENTESTING READY)

* **ZERO CREDENTIALS IN REPO:** Está ESTRICTAMENTE PROHIBIDO guardar archivos `.json` de credenciales de Google (Service Accounts) en el código fuente o en la imagen Docker.
* **Authentication Flow:** Las credenciales de Google deben pasarse a través de variables de entorno. Usa una variable como `GOOGLE_CREDENTIALS_JSON` que reciba el string JSON (o en base64) al momento de hacer `docker run`, y que Python la lea usando `json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))` para construir las credenciales en memoria usando `service_account.Credentials.from_service_account_info()`.
* **Docker Security:** * Usa una imagen base oficial y ligera (ej. `python:3.11-slim`).
    * No ejecutes el contenedor como root (crea un usuario y grupo específico en el Dockerfile).
    * Asegúrate de no dejar puertos innecesarios expuestos.
* **Data Sanitization:** Aplica sanitización y validación estricta a cada campo de Pydantic. Usa expresiones regulares para campos como Códigos Postales, Fechas y CUV.

## Output Request for the Agent
Por favor, genera el proyecto con la siguiente estructura de archivos y proporciona el código completo para cada uno:
1. `main.py` (App FastAPI, endpoints y lógica orquestadora).
2. `schemas.py` (Modelos Pydantic).
3. `pdf_service.py` (Lógica de creación del PDF).
4. `drive_service.py` (Lógica de subida y creación de carpetas en GDrive).
5. `bq_service.py` (Lógica de inserción en BigQuery).
6. `Dockerfile` (Configurado con seguridad y usuario no root).
7. `requirements.txt` (Dependencias).
8. `README.md` (Instrucciones de cómo levantar el contenedor pasando la variable de entorno de las credenciales).