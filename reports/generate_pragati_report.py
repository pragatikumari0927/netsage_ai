from pathlib import Path
import re

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

REPORTS_DIR = Path(__file__).resolve().parent
SOURCE_PATH = REPORTS_DIR / "Pragati_Kumari_Report.md"
OUTPUT_PATH = REPORTS_DIR / "Pragati_Kumari_Report.docx"


def set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def add_bullets(document: Document, text: str) -> None:
    for item in text.split("; "):
        paragraph = document.add_paragraph(style="List Bullet")
        add_inline_markup(paragraph, item)


def add_inline_markup(paragraph, text: str) -> None:
    parts = re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        run = paragraph.add_run(part.strip("`"))
        if part.startswith("`"):
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif part.startswith("**"):
            run.bold = True
            run.text = part[2:-2]


def add_table(document: Document, lines: list[str]) -> None:
    rows = []
    for line in lines:
        values = [value.strip() for value in line.strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-+:?", value.replace(" ", "")) for value in values):
            rows.append(values)

    if not rows:
        return

    table = document.add_table(rows=1, cols=len(rows[0]))
    table.style = "Light Shading Accent 1"
    header_cells = table.rows[0].cells
    for index, value in enumerate(rows[0]):
        header_cells[index].text = value
        set_cell_shading(header_cells[index], "1F4E78")
        for run in header_cells[index].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.bold = True

    for row in rows[1:]:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].text = value


def configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)

    for style_name, size, color in (("Title", 22, "17365D"), ("Heading 1", 16, "17365D"), ("Heading 2", 13, "1F4E78")):
        style = document.styles[style_name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)


def build_document(markdown: str) -> Document:
    document = Document()
    configure_document(document)
    lines = markdown.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if not line or line == "---":
            index += 1
            continue
        if line.startswith("# "):
            paragraph = document.add_paragraph(style="Title")
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline_markup(paragraph, line[2:])
        elif line.startswith("## "):
            document.add_heading(line[3:], level=1)
        elif line.startswith("### "):
            document.add_heading(line[4:], level=2)
        elif line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            add_table(document, table_lines)
            continue
        elif re.match(r"^\d+\. ", line):
            paragraph = document.add_paragraph(style="List Number")
            add_inline_markup(paragraph, re.sub(r"^\d+\. ", "", line))
        elif line.startswith("- "):
            paragraph = document.add_paragraph(style="List Bullet")
            add_inline_markup(paragraph, line[2:])
        elif line.startswith("**Troubleshooting case"):
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline_markup(paragraph, line)
        else:
            paragraph = document.add_paragraph()
            add_inline_markup(paragraph, line)
        index += 1

    return document


def main() -> None:
    document = build_document(SOURCE_PATH.read_text(encoding="utf-8"))
    document.core_properties.title = "NetSage AI — Pragati Kumari"
    document.core_properties.author = "Pragati Kumari"
    document.core_properties.subject = "Cisco VIP Internship Project Report"
    document.save(OUTPUT_PATH)


if __name__ == "__main__":
    main()
