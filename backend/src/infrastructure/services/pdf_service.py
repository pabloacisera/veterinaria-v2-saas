import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


class PDFService:

    def generate_factura(self, data: dict) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=20*mm, bottomMargin=20*mm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="FacturaTitle", fontSize=18, spaceAfter=10, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="FacturaSubtitle", fontSize=10, spaceAfter=4, textColor=colors.gray))
        styles.add(ParagraphStyle(name="HeaderField", fontSize=9, spaceAfter=2))
        styles.add(ParagraphStyle(name="HeaderValue", fontSize=10, spaceAfter=2, fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(name="TableHeader", fontSize=9, fontName="Helvetica-Bold", alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableCell", fontSize=9, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableCellLeft", fontSize=9))
        styles.add(ParagraphStyle(name="TotalLabel", fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name="TotalValue", fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT))

        story = []

        story.append(Paragraph("FACTURA", styles["FacturaTitle"]))
        story.append(Paragraph(f"Nº {data.get('numero_factura', '')}", styles["FacturaSubtitle"]))
        story.append(Spacer(1, 5*mm))

        company = data.get("company", {})
        client = data.get("client", {})
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M")

        header_data = [
            [Paragraph("VENDEDOR", styles["HeaderField"]),
             Paragraph("CLIENTE", styles["HeaderField"])],
            [Paragraph(f"<b>{company.get('name', '')}</b>", styles["HeaderValue"]),
             Paragraph(f"<b>{client.get('name', '')}</b>", styles["HeaderValue"])],
            [Paragraph(f"CUIT: {company.get('cuit', '')}", styles["HeaderField"]),
             Paragraph(f"CUIT/DNI: {client.get('doc', '')}", styles["HeaderField"])],
            [Paragraph(f"Dirección: {company.get('address', '')}", styles["HeaderField"]),
             Paragraph(f"Dirección: {client.get('address', '')}", styles["HeaderField"])],
            [Paragraph(f"Fecha: {now}", styles["HeaderField"]), ""],
        ]
        t = Table(header_data, colWidths=[80*mm, 80*mm])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("SPAN", (0, 0), (0, 0)),
            ("SPAN", (1, 0), (1, 0)),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 5*mm))

        items = data.get("items", [])
        table_data = [
            [Paragraph("Cant.", styles["TableHeader"]),
             Paragraph("Descripción", styles["TableHeader"]),
             Paragraph("P. Unit.", styles["TableHeader"]),
             Paragraph("Subtotal", styles["TableHeader"])],
        ]
        for item in items:
            table_data.append([
                Paragraph(str(item.get("quantity", "")), styles["TableCell"]),
                Paragraph(item.get("description", ""), styles["TableCellLeft"]),
                Paragraph(f"$ {item.get('unit_price', 0):,.2f}", styles["TableCell"]),
                Paragraph(f"$ {item.get('subtotal', 0):,.2f}", styles["TableCell"]),
            ])

        col_widths = [18*mm, 82*mm, 30*mm, 30*mm]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.15, 0.34, 0.60)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(Spacer(1, 3*mm))

        subtotal = data.get("subtotal", 0)
        iva_amount = data.get("iva_amount", 0)
        total = data.get("total", 0)
        iva_enabled = data.get("iva_enabled", True)

        totals_data = []
        totals_data.append([
            Paragraph("Subtotal:", styles["TotalLabel"]),
            Paragraph(f"$ {subtotal:,.2f}", styles["TotalValue"]),
        ])
        if iva_enabled:
            totals_data.append([
                Paragraph("IVA 21%:", styles["TotalLabel"]),
                Paragraph(f"$ {iva_amount:,.2f}", styles["TotalValue"]),
            ])
        totals_data.append([
            Paragraph("TOTAL:", styles["TotalLabel"]),
            Paragraph(f"$ {total:,.2f}", styles["TotalValue"]),
        ])
        t = Table(totals_data, colWidths=[130*mm, 30*mm])
        t.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.grey),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ]))
        story.append(t)

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def generate_prescripcion(self, data: dict) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=20*mm, bottomMargin=20*mm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="PrescTitle", fontSize=18, spaceAfter=10, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="PrescSubtitle", fontSize=10, spaceAfter=4, textColor=colors.gray))
        styles.add(ParagraphStyle(name="Field", fontSize=10, spaceAfter=2))
        styles.add(ParagraphStyle(name="Value", fontSize=11, spaceAfter=6, fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(name="SectionTitle", fontSize=12, fontName="Helvetica-Bold",
                                   spaceBefore=8, spaceAfter=4, textColor=colors.Color(0.15, 0.34, 0.60)))
        styles.add(ParagraphStyle(name="TreatmentText", fontSize=11, spaceAfter=10,
                                   leftIndent=10, borderWidth=1, borderColor=colors.grey,
                                   borderPadding=6))
        styles.add(ParagraphStyle(name="TableHeaderP", fontSize=9, fontName="Helvetica-Bold", alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableCellP", fontSize=9, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableCellLeftP", fontSize=9))

        story = []

        story.append(Paragraph("PRESCRIPCIÓN MÉDICA", styles["PrescTitle"]))
        story.append(Paragraph(f"Fecha: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}", styles["PrescSubtitle"]))
        story.append(Spacer(1, 5*mm))

        company = data.get("company", {})
        story.append(Paragraph(f"{company.get('name', '')}", styles["Value"]))
        story.append(Paragraph(f"Profesional: {company.get('professional_name', '')}", styles["Field"]))
        story.append(Paragraph(f"Matrícula: {company.get('license', '')}", styles["Field"]))
        story.append(Paragraph(f"CUIT: {company.get('cuit', '')}", styles["Field"]))
        story.append(Spacer(1, 3*mm))

        pet = data.get("pet", {})
        story.append(Paragraph("PACIENTE", styles["SectionTitle"]))
        story.append(Paragraph(f"Nombre: {pet.get('name', '')}", styles["Value"]))
        story.append(Paragraph(f"Especie: {pet.get('species', '')} | Raza: {pet.get('breed', '')} | Sexo: {pet.get('sex', '')}", styles["Field"]))
        story.append(Spacer(1, 3*mm))

        owner = data.get("owner", {})
        if owner.get("name"):
            story.append(Paragraph("PROPIETARIO", styles["SectionTitle"]))
            story.append(Paragraph(f"{owner.get('name', '')} — {owner.get('doc', '')}", styles["Field"]))
            story.append(Spacer(1, 3*mm))

        story.append(Paragraph("DIAGNÓSTICO", styles["SectionTitle"]))
        story.append(Paragraph(data.get("diagnosis", ""), styles["Field"]))
        story.append(Spacer(1, 3*mm))

        treatment = data.get("treatment", "")
        if treatment:
            story.append(Paragraph("TRATAMIENTO", styles["SectionTitle"]))
            story.append(Paragraph(treatment, styles["TreatmentText"]))

        procedures = data.get("procedures", [])
        if procedures:
            story.append(Paragraph("PROCEDIMIENTOS", styles["SectionTitle"]))
            proc_table = [
                [Paragraph("Procedimiento", styles["TableHeaderP"]),
                 Paragraph("Cant.", styles["TableHeaderP"]),
                 Paragraph("P. Unit.", styles["TableHeaderP"])],
            ]
            for p in procedures:
                proc_table.append([
                    Paragraph(p.get("name", ""), styles["TableCellLeftP"]),
                    Paragraph(str(p.get("quantity", "")), styles["TableCellP"]),
                    Paragraph(f"$ {p.get('price', 0):,.2f}", styles["TableCellP"]),
                ])
            t = Table(proc_table, colWidths=[70*mm, 20*mm, 30*mm])
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.15, 0.34, 0.60)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]))
            story.append(t)

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
