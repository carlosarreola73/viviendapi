from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from io import BytesIO
from app.schemas.poliza import PolizaPayload
import qrcode
from PIL import Image as PILImage

class PDFGenerator:
    @staticmethod
    def generate_policy_pdf(data: PolizaPayload, qr_url: str = None) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#1A237E"),
            alignment=1,
            spaceAfter=20
        )
        
        elements = []
        
        # Título
        elements.append(Paragraph("CERTIFICADO DE PÓLIZA DE VIVIENDA", title_style))
        elements.append(Spacer(1, 12))
        
        # Datos Principales
        main_data = [
            ["Beneficiario:", data.nombre_beneficiario],
            ["Número de Crédito:", data.numero_credito],
            ["CUV:", data.cuv],
            ["Póliza:", data.poliza],
            ["Certificado:", data.numero_certificado]
        ]
        
        t = Table(main_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#E8EAF6")),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1A237E")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Dirección
        elements.append(Paragraph("DIRECCIÓN DE LA VIVIENDA", styles['Heading2']))
        dir_data = [
            ["Domicilio:", data.direccion_vivienda.domicilio],
            ["Colonia:", data.direccion_vivienda.colonia],
            ["CP:", data.direccion_vivienda.codigo_postal],
            ["Municipio/Estado:", f"{data.direccion_vivienda.municipio}, {data.direccion_vivienda.estado}"]
        ]
        t_dir = Table(dir_data, colWidths=[100, 350])
        elements.append(t_dir)
        elements.append(Spacer(1, 20))
        
        # Código QR (Si se proporciona el URL)
        if qr_url:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar QR en un buffer temporal
            qr_buffer = BytesIO()
            img_qr.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # Añadir imagen al PDF
            qr_img_platypus = Image(qr_buffer, width=100, height=100)
            qr_img_platypus.hAlign = 'RIGHT'
            elements.append(qr_img_platypus)
            elements.append(Paragraph(f"Escanea para verificar el certificado online", styles['Italic']))

        # Sello Digital
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("SELLO DIGITAL DE VALIDACIÓN", styles['Heading3']))
        elements.append(Paragraph(data.sello_digital, styles['Code']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
