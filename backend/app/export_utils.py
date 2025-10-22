import io
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def generate_excel(data):
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Soportes"

    # Agregar encabezados
    headers = list(data[0].keys())
    ws.append(headers)

    # Agregar datos
    for row in data:
        ws.append(list(row.values()))

    wb.save(output)
    output.seek(0)
    return output

def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Preparar datos para la tabla
    table_data = [list(data[0].keys())]  # Encabezados
    for row in data:
        table_data.append(list(row.values()))

    # Crear tabla
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(t)
    doc.build(elements)

    buffer.seek(0)
    return buffer