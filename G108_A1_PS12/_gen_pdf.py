from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, HRFlowable
from reportlab.lib.enums import TA_JUSTIFY
import re

content = open('designPS12_G108.md', encoding='utf-8').read()

doc = SimpleDocTemplate(
    'designPS12_G108.pdf',
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=14, spaceAfter=6,
                             textColor=colors.HexColor('#1F4E79'))
h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=12, spaceAfter=4,
                           textColor=colors.HexColor('#1F4E79'), spaceBefore=10)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10.5, spaceAfter=3,
                           textColor=colors.HexColor('#2E75B6'), spaceBefore=8)
body_style = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=9, leading=13,
                             spaceAfter=4, alignment=TA_JUSTIFY)
code_style = ParagraphStyle('Code2', parent=styles['Code'], fontSize=8, leading=11,
                             fontName='Courier', backColor=colors.HexColor('#F2F2F2'),
                             leftIndent=10, spaceAfter=4)

FENCE = '```'

story = []
in_code = False
code_lines = []

for line in content.splitlines():
    if line.startswith(FENCE):
        if in_code:
            story.append(Preformatted('\n'.join(code_lines), code_style))
            code_lines = []
            in_code = False
        else:
            in_code = True
        continue
    if in_code:
        code_lines.append(line)
        continue
    if line.startswith('# '):
        story.append(Paragraph(line[2:], title_style))
        story.append(HRFlowable(width='100%', thickness=1,
                                color=colors.HexColor('#1F4E79'), spaceAfter=6))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], h1_style))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], h2_style))
    elif line.strip() == '':
        story.append(Spacer(1, 0.15*cm))
    else:
        safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
        safe = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', safe)
        story.append(Paragraph(safe, body_style))

doc.build(story)
print('designPS12_G108.pdf created.')
