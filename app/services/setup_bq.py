from google.cloud import bigquery
from app.core.config import settings
import json

def create_vivienda_tables():
    info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
    client = bigquery.Client.from_service_account_info(info)
    
    dataset_id = settings.BQ_DATASET
    dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
    dataset.location = "US"
    
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {client.project}.{dataset_id} verificado/creado.")
    
    # 1. Tabla de Certificados (Existente)
    table_id = settings.BQ_TABLE
    schema = [
        bigquery.SchemaField("nombre_beneficiario", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("numero_credito", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("cuv", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("poliza", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("numero_certificado", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("nombre_asegurado", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("valor_avaluo", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("url_pdf_drive", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("fecha_registro", "TIMESTAMP", mode="REQUIRED", default_value_expression="CURRENT_TIMESTAMP"),
    ]
    
    table_ref = dataset.table(table_id)
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table, exists_ok=True)
    print(f"Tabla {table_id} verificada/creada exitosamente.")

    # 2. Nueva Tabla: Poliza Padre
    master_table_id = "poliza_padre"
    master_schema = [
        bigquery.SchemaField("uid", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("poliza", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("inicio_vigencia", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("fin_vigencia", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("fecha_registro", "TIMESTAMP", mode="REQUIRED", default_value_expression="CURRENT_TIMESTAMP"),
    ]
    
    master_table_ref = dataset.table(master_table_id)
    master_table = bigquery.Table(master_table_ref, schema=master_schema)
    master_table = client.create_table(master_table, exists_ok=True)
    print(f"Tabla {master_table_id} verificada/creada exitosamente.")

if __name__ == "__main__":
    create_vivienda_tables()
