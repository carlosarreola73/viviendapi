from google.cloud import bigquery
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self):
        if not settings.GOOGLE_CREDENTIALS_JSON:
            raise ValueError("GOOGLE_CREDENTIALS_JSON is not set in settings")
        
        info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
        self.client = bigquery.Client.from_service_account_info(info)
        self.dataset_id = settings.BQ_DATASET
        self.table_id = settings.BQ_TABLE

    def log_policy(self, data, pdf_url: str):
        table_ref = f"{self.client.project}.{self.dataset_id}.{self.table_id}"
        
        row_to_insert = {
            "nombre_beneficiario": data.nombre_beneficiario,
            "numero_credito": data.numero_credito,
            "cuv": data.cuv,
            "poliza": data.poliza,
            "numero_certificado": data.numero_certificado,
            "nombre_asegurado": data.nombre_asegurado,
            "valor_avaluo": data.valor_avaluo,
            "url_pdf_drive": pdf_url
        }
        
        errors = self.client.insert_rows_json(table_ref, [row_to_insert])
        if errors:
            raise RuntimeError(f"BigQuery insertion errors: {errors}")

    def list_policies(self, limit: int = 100):
        table_ref = f"{self.client.project}.{self.dataset_id}.{self.table_id}"
        query = f"SELECT * FROM `{table_ref}` ORDER BY fecha_registro DESC LIMIT {limit}"
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row.items()) for row in results]

    def log_poliza_padre(self, uid: str, data):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        
        row_to_insert = {
            "uid": uid,
            "poliza": data.poliza,
            "inicio_vigencia": str(data.inicio_vigencia),
            "fin_vigencia": str(data.fin_vigencia)
        }
        
        errors = self.client.insert_rows_json(table_ref, [row_to_insert])
        if errors:
            raise RuntimeError(f"BigQuery insertion errors (padre): {errors}")

    def list_polizas_padre(self, limit: int = 100):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        query = f"SELECT * FROM `{table_ref}` ORDER BY fecha_registro DESC LIMIT {limit}"
        query_job = self.client.query(query)
        return [dict(row.items()) for row in query_job.result()]

    def get_poliza_padre(self, uid: str):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        query = f"SELECT * FROM `{table_ref}` WHERE uid = @uid LIMIT 1"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("uid", "STRING", uid)]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job.result())
        return dict(results[0].items()) if results else None

    def update_poliza_padre(self, uid: str, data):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        query = f"""
            UPDATE `{table_ref}`
            SET poliza = @poliza,
                inicio_vigencia = @inicio,
                fin_vigencia = @fin
            WHERE uid = @uid
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("poliza", "STRING", data.poliza),
                bigquery.ScalarQueryParameter("inicio", "DATE", data.inicio_vigencia),
                bigquery.ScalarQueryParameter("fin", "DATE", data.fin_vigencia),
                bigquery.ScalarQueryParameter("uid", "STRING", uid),
            ]
        )
        self.client.query(query, job_config=job_config).result()

    def delete_poliza_padre(self, uid: str):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        query = f"DELETE FROM `{table_ref}` WHERE uid = @uid"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("uid", "STRING", uid)]
        )
        self.client.query(query, job_config=job_config).result()

    def get_poliza_padre_by_name(self, poliza_name: str):
        table_id = "poliza_padre"
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        query = f"SELECT * FROM `{table_ref}` WHERE poliza = @name LIMIT 1"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", poliza_name)]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job.result())
        return dict(results[0].items()) if results else None
