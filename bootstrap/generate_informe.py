#!/usr/bin/env python3
"""Genera informe.pdf con documentación de los 12 KPIs."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kpi_definitions import DASHBOARD_NAME, GRADER_EMAIL, KPIS  # noqa: E402


def build_pdf(output: Path) -> None:
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor("#1a365d"),
    )
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6)
    sql_style = ParagraphStyle(
        "SQL",
        parent=styles["Code"],
        fontSize=7,
        leading=9,
        fontName="Courier",
        backColor=colors.HexColor("#f7fafc"),
        borderPadding=6,
        spaceAfter=10,
    )

    story = []
    story.append(Paragraph("Lab 7 — Visualización de Datos", title_style))
    story.append(
        Paragraph(
            f"<b>RetailMax</b> | Área: Estrategia y Expansión Comercial<br/>"
            f"Dashboard: {DASHBOARD_NAME}<br/>"
            f"Usuario de calificación: {GRADER_EMAIL}",
            body,
        )
    )
    story.append(Spacer(1, 0.2 * inch))

    for i, kpi in enumerate(KPIS, 1):
        story.append(Paragraph(f"Indicador {i}: {kpi['name']}", h2))
        story.append(Paragraph(f"<b>Tab:</b> {kpi['tab']}", body))
        story.append(
            Paragraph(f"<b>1. Nombre del indicador:</b> {kpi['name']}", body)
        )
        story.append(
            Paragraph(
                f"<b>2. Qué representa en términos de negocio:</b> {kpi['business']}",
                body,
            )
        )
        story.append(
            Paragraph(
                f"<b>3. Por qué es importante para el área:</b> {kpi['importance']}",
                body,
            )
        )
        story.append(
            Paragraph(
                f"<b>4. Visualización usada y justificación:</b> "
                f"{kpi['display'].upper()} — {kpi['viz_why']}",
                body,
            )
        )
        sql_escaped = (
            kpi["sql"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        story.append(Paragraph("<b>5. Consulta SQL completa:</b>", body))
        story.append(Paragraph(f"<pre>{sql_escaped}</pre>", sql_style))

    doc.build(story)


if __name__ == "__main__":
    out = ROOT / "informe.pdf"
    build_pdf(out)
    print(f"Generado: {out}")
