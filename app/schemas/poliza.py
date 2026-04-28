from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
import re

class CoberturaDates(BaseModel):
    desde: date
    hasta: date

class CoberturasVigencias(BaseModel):
    estructura_10_anios: CoberturaDates = Field(..., alias="Estructura (10 años)")
    impermeabilizacion_5_anios: CoberturaDates = Field(..., alias="Impermeabilización (5 años)")
    instalaciones_2_anios: CoberturaDates = Field(..., alias="Instalaciones (2 años)")

    class Config:
        populate_by_name = True

class DireccionVivienda(BaseModel):
    domicilio: str = Field(..., min_length=5, max_length=200)
    colonia: str = Field(..., min_length=2, max_length=100)
    codigo_postal: str = Field(..., pattern=r"^\d{5}$")
    municipio: str = Field(..., min_length=2, max_length=100)
    estado: str = Field(..., min_length=2, max_length=100)

class PolizaPayload(BaseModel):
    nombre_beneficiario: str = Field(..., min_length=2, max_length=150)
    numero_credito: str = Field(..., min_length=5, max_length=50)
    cuv: str = Field(..., pattern=r"^[A-Z0-9]{16}$")
    poliza: str = Field(..., min_length=5, max_length=50)
    direccion_vivienda: DireccionVivienda
    numero_certificado: str = Field(..., min_length=5, max_length=50)
    nombre_asegurado: str = Field(..., min_length=2, max_length=150)
    valor_avaluo: float = Field(..., gt=0)
    coberturas_vigencias: CoberturasVigencias
    sello_digital: str = Field(..., min_length=10)

    @field_validator('nombre_beneficiario', 'nombre_asegurado', mode='before')
    @classmethod
    def sanitize_names(cls, v):
        if isinstance(v, str):
            return re.sub(r'<[^>]*?>', '', v)
        return v

class PolizaResponse(BaseModel):
    data: PolizaPayload
    url_visualizacion: str
    url_descarga_directa: str
    status: str = "success"

class PolizaListResponse(BaseModel):
    total: int
    items: list[dict]
    status: str = "success"

class PolizaPadrePayload(BaseModel):
    poliza: str = Field(..., min_length=5)
    inicio_vigencia: date
    fin_vigencia: date
