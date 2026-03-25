"""
============================================================
  report.py  —  PDF Report Generator
============================================================

This file takes the audit results from checker.py and creates
a professional-looking PDF report that can be saved and shared.

HOW IT WORKS:
    We use the "reportlab" library to draw text, shapes, and
    colors onto a PDF canvas — like a digital paintbrush.

USAGE:
    from report import generate_pdf_report
    path = generate_pdf_report(audit_results, "output_folder")
"""

import os
from datetime import datetime

# reportlab is a Python library for creating PDF files
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ──────────────────────────────────────────────
# COLOR PALETTE — define our brand colors once
# ──────────────────────────────────────────────

COLOR_PRIMARY    = colors.HexColor("#1a73e8")   # Google blue — for headings
COLOR_SUCCESS    = colors.HexColor("#34a853")   # Green — for good results
COLOR_WARNING    = colors.HexColor("#fbbc04")   # Yellow — for warnings
COLOR_DANGER     = colors.HexColor("#ea4335")   # Red — for bad results
COLOR_DARK       = colors.HexColor("#202124")   # Near-black — for body text
COLOR_LIGHT_GRAY = colors.HexColor("#f1f3f4")   # Light gray — for backgrounds
COLOR_WHITE      = colors.white


def get_score_color(score: int) -> object:
    """Returns a color based on how good the score is."""
    if score >= 70:
        return COLOR_SUCCESS   # Green for good
    elif score >= 40:
        return COLOR_WARNING   # Yellow for average
    else:
        return COLOR_DANGER    # Red for poor


def bool_to_label(value: bool, true_label="Yes ✓", false_label="No ✗") -> str:
    """Converts True/False into a readable Yes/No label."""
    return true_label if value else false_label


def generate_pdf_report(audit: dict, output_dir: str = ".") -> str:
    """
    Creates a full PDF audit report and saves it to disk.

    Parameters:
        audit (dict):       The complete result from run_full_audit()
        output_dir (str):   Folder where the PDF should be saved

    Returns:
        str: The full file path of the saved PDF
    """

    # ── Build the output file path ──
    # Replace spaces and special chars in business name for a clean filename
    safe_name = audit["business_name"].replace(" ", "_").replace("/", "-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"audit_{safe_name}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    # ── Set up the PDF document ──
    # SimpleDocTemplate handles page layout, margins, and page breaks for us
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # ── Set up text styles ──
    # Styles control font, size, color, and alignment of text
    base_styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "CustomTitle",
        parent=base_styles["Title"],
        fontSize=22,
        textColor=COLOR_PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER
    )

    style_subtitle = ParagraphStyle(
        "CustomSubtitle",
        parent=base_styles["Normal"],
        fontSize=11,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    style_section = ParagraphStyle(
        "SectionHeader",
        parent=base_styles["Heading2"],
        fontSize=13,
        textColor=COLOR_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        borderPad=4
    )

    style_body = ParagraphStyle(
        "BodyText",
        parent=base_styles["Normal"],
        fontSize=10,
        textColor=COLOR_DARK,
        spaceAfter=4,
        leading=16   # Line height
    )

    style_tip = ParagraphStyle(
        "TipText",
        parent=base_styles["Normal"],
        fontSize=10,
        textColor=COLOR_DARK,
        spaceAfter=8,
        leftIndent=10,
        leading=15
    )

    # ── story = the list of elements that go into our PDF ──
    # We "append" things to this list and reportlab lays them out automatically
    story = []

    # ════════════════════════════════════════
    # HEADER SECTION
    # ════════════════════════════════════════

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("🏪 Digital Health Report", style_title))
    story.append(Paragraph(
        f"{audit['business_name']} &bull; {audit['city']} &bull; "
        f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        style_subtitle
    ))

    # Horizontal divider line
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARY, spaceAfter=16))

    # ════════════════════════════════════════
    # SCORE SUMMARY BOX
    # ════════════════════════════════════════

    score = audit["score"]
    score_color = get_score_color(score["total"])

    # We create a TABLE with one row to make a colored "score card"
    score_table_data = [[
        Paragraph(f'<font size="36" color="{score_color.hexval()}"><b>{score["total"]}</b></font><font size="14" color="gray">/100</font>', style_body),
        Paragraph(
            f'<font size="28" color="{score_color.hexval()}"><b>{score["grade"]}</b></font><br/>'
            f'<font size="11" color="#555555">{score["summary"]}</font>',
            style_body
        ),
        Paragraph(
            f'<font size="11"><b>Google:</b> {score["google_score"]}/40<br/>'
            f'<b>Website:</b> {score["website_score"]}/40<br/>'
            f'<b>Social:</b> {score["social_score"]}/20</font>',
            style_body
        )
    ]]

    score_table = Table(score_table_data, colWidths=[4*cm, 8*cm, 5*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), COLOR_LIGHT_GRAY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLOR_LIGHT_GRAY]),
        ("BOX",         (0, 0), (-1, -1), 1.5, COLOR_PRIMARY),
        ("ROUNDEDCORNERS", [6]),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (0, -1), "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # ════════════════════════════════════════
    # SECTION 1 — GOOGLE PRESENCE
    # ════════════════════════════════════════

    story.append(Paragraph("📡 Google Presence", style_section))

    google = audit["google"]
    google_rows = [
        ["Check",                          "Result"],
        ["Appears in Google Search",        bool_to_label(google.get("found", False))],
        ["Times business name appeared",    str(google.get("result_count", 0))],
        ["Has Google Knowledge Panel",      bool_to_label(google.get("has_knowledge_panel", False))],
    ]
    story.append(_make_table(google_rows))

    # ════════════════════════════════════════
    # SECTION 2 — WEBSITE HEALTH
    # ════════════════════════════════════════

    story.append(Paragraph("🌐 Website Health", style_section))

    website = audit["website"]
    if website.get("accessible"):
        web_rows = [
            ["Check",              "Result"],
            ["Website accessible", "Yes ✓"],
            ["HTTP Status Code",   str(website.get("status_code", "N/A"))],
            ["Uses HTTPS (secure)",bool_to_label(website.get("uses_https", False))],
            ["Load Speed",         f'{website.get("load_time", "?")}s — {website.get("speed_rating", "?")}'],
            ["Mobile Friendly",    bool_to_label(website.get("is_mobile_friendly", False))],
            ["Has Page Title",     bool_to_label(website.get("has_title", False))],
            ["Phone Number Found", bool_to_label(website.get("has_phone", False))],
            ["Email Found",        bool_to_label(website.get("has_email", False))],
        ]
        if website.get("page_title"):
            web_rows.append(["Page Title", website.get("page_title", "None")])
    else:
        # Website couldn't be reached
        web_rows = [
            ["Check", "Result"],
            ["Website accessible", f'No ✗ — {website.get("error", "Unknown error")}'],
        ]

    story.append(_make_table(web_rows))

    # ════════════════════════════════════════
    # SECTION 3 — SOCIAL MEDIA
    # ════════════════════════════════════════

    story.append(Paragraph("📱 Social Media Presence", style_section))

    social = audit["social"]
    social_rows = [["Platform", "Profile Likely Exists", "URL Checked"]]
    for platform, info in social.items():
        social_rows.append([
            platform,
            bool_to_label(info.get("likely_exists", False)),
            info.get("checked_url", "N/A")
        ])
    story.append(_make_table(social_rows, col_widths=[3*cm, 4*cm, 10*cm]))

    # ════════════════════════════════════════
    # SECTION 4 — RECOMMENDATIONS
    # ════════════════════════════════════════

    story.append(Paragraph("💡 Recommendations", style_section))
    story.append(Paragraph(
        "These are prioritized action items based on your audit results:",
        style_body
    ))
    story.append(Spacer(1, 0.2*cm))

    for tip in audit["recommendations"]:
        story.append(Paragraph(f"• {tip}", style_tip))

    # ════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.3*cm))

    footer_style = ParagraphStyle(
        "Footer",
        parent=base_styles["Normal"],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "Generated by Digital Health Checker | "
        "Data is approximate and based on publicly available information.",
        footer_style
    ))

    # ── Build the PDF (this is where reportlab actually creates the file) ──
    doc.build(story)

    print(f"  📄 PDF saved to: {filepath}")
    return filepath


def _make_table(rows: list, col_widths: list = None) -> Table:
    """
    Helper function to create a nicely styled data table.

    Parameters:
        rows (list): 2D list — first row is header, rest are data
        col_widths (list): Optional custom widths for each column

    Returns:
        Table: A styled reportlab Table object
    """

    # Convert all cell values to strings (Table needs strings)
    cleaned = [[str(cell) for cell in row] for row in rows]

    # Default: split width evenly among columns
    if col_widths is None:
        num_cols = len(cleaned[0])
        col_widths = [17*cm / num_cols] * num_cols

    table = Table(cleaned, colWidths=col_widths)
    table.setStyle(TableStyle([
        # Header row styling
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),

        # Data rows styling
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 1), (-1, -1), COLOR_DARK),

        # Alternating row colors (zebra striping)
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [COLOR_WHITE, COLOR_LIGHT_GRAY]),

        # Borders
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BOX",           (0, 0), (-1, -1), 1, colors.lightgrey),

        # Padding inside cells
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),

        # First column bold (it's always the label)
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
    ]))

    return table
