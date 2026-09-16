from datetime import date
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ESTADO_GUIA_LABEL = {
    "EN_VENTA": "En venta",
    "PENDIENTE_LIQUIDACION": "Pendiente de liquidación",
    "PARCIALMENTE_LIQUIDADA": "Parcialmente liquidada",
}


def _dias_transcurridos(fecha: date) -> int:
    return (date.today() - fecha).days


def _rango_texto(desde: date | None, hasta: date | None) -> str:
    if desde and hasta:
        return f"Del {desde.isoformat()} al {hasta.isoformat()}"
    if desde:
        return f"Desde {desde.isoformat()}"
    if hasta:
        return f"Hasta {hasta.isoformat()}"
    return "Todas las fechas"


def generar_pdf_detalle_por_agencia(
    data: dict,
    desde: date | None,
    hasta: date | None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("titulo", parent=styles["Title"], fontSize=18, spaceAfter=2)
    subtitulo_style = ParagraphStyle(
        "subtitulo", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#5b6b8c")
    )
    agencia_style = ParagraphStyle("agencia", parent=styles["Heading2"], fontSize=13, spaceAfter=2)
    cuadro_style = ParagraphStyle("cuadro", parent=styles["Normal"], fontSize=6.5, alignment=1, leading=9)

    elementos = [
        Paragraph("Detalle por agencia", titulo_style),
        Paragraph(f"Rango de fechas: {_rango_texto(desde, hasta)}", subtitulo_style),
        Paragraph(f"Generado el {date.today().isoformat()}", subtitulo_style),
        Spacer(1, 8 * mm),
    ]

    # ==========================
    # Calcular totales por estado (mismas reglas que el dashboard)
    # ==========================

    en_venta = Decimal("0.00")
    proximas = Decimal("0.00")
    vencidas = Decimal("0.00")
    parcial = Decimal("0.00")

    for grupo in data["grupos"]:
        for detalle in grupo["detalles"]:
            dias = _dias_transcurridos(detalle["fecha"])
            monto = detalle["x_estimado"]
            if detalle["estado_guia"] == "PARCIALMENTE_LIQUIDADA":
                parcial += monto
            elif dias > 30:
                vencidas += monto
            elif dias >= 25:
                proximas += monto
            else:
                en_venta += monto

    total_general = data["total_general"]

    cuadros = [
        ("EN VENTA", en_venta, "168264"),
        ("PRÓXIMAS A VENCER (25-30 DÍAS)", proximas, "a3620a"),
        ("VENCIDAS (+30 DÍAS)", vencidas, "b3261e"),
        ("PARCIALMENTE LIQUIDADAS", parcial, "b3261e"),
        ("TOTAL ESTIMADO GENERAL", total_general, "2457c5"),
    ]

    celdas = [
        [
            Paragraph(
                f'{label}<br/><br/><font size=13 color="#{color_hex}"><b>S/ {monto:.2f}</b></font>',
                cuadro_style,
            )
            for label, monto, color_hex in cuadros
        ]
    ]
    tabla_totales = Table(celdas, colWidths=[34.4 * mm] * 5)
    tabla_totales.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#dfe6f4")),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#dfe6f4")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabla_totales)
    elementos.append(Spacer(1, 10 * mm))

    # ==========================
    # Un cuadro por agencia
    # ==========================

    for grupo in data["grupos"]:
        elementos.append(Paragraph(grupo["agencia"], agencia_style))
        elementos.append(
            Paragraph(f'Total entregado (estimado): S/ {grupo["total_entregado"]:.2f}', subtitulo_style)
        )
        elementos.append(Spacer(1, 2 * mm))

        filas = [["N° Guía", "Fecha", "Producto", "Estado", "Cant.", "P. público", "P. agencia", "50% est."]]
        for detalle in grupo["detalles"]:
            filas.append(
                [
                    detalle["numero_guia"],
                    detalle["fecha"].isoformat(),
                    detalle["producto"],
                    ESTADO_GUIA_LABEL.get(detalle["estado_guia"], detalle["estado_guia"]),
                    f'{detalle["cantidad"]:.0f}',
                    f'S/ {detalle["precio_publico"]:.2f}',
                    f'S/ {detalle["precio_agencia"]:.2f}',
                    f'S/ {detalle["x_estimado"]:.2f}',
                ]
            )

        tabla = Table(
            filas,
            colWidths=[18 * mm, 18 * mm, 38 * mm, 30 * mm, 12 * mm, 20 * mm, 20 * mm, 20 * mm],
            repeatRows=1,
        )
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3ff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#163c96")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dfe6f4")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elementos.append(tabla)
        elementos.append(Spacer(1, 8 * mm))

    doc.build(elementos)
    return buffer.getvalue()
