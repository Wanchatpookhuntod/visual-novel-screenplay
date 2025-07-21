"""
Test Screenplay PDF Formatting for A4
Tests the new professional screenplay formatting standards
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from font_manager import font_manager


def test_screenplay_formatting():
    """Test the new screenplay formatting with sample content"""
    print("Testing Professional Screenplay Formatting for A4...")
    
    # Register fonts
    fonts_registered = font_manager.register_thai_fonts()
    font_family = font_manager.get_primary_thai_font()
    print(f"Using font: {font_family}")
    
    # Create test PDF
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'screenplay_format_test.pdf')
    
    # Document with screenplay margins
    doc = SimpleDocTemplate(
        test_pdf_path, 
        pagesize=A4, 
        topMargin=1*inch, 
        bottomMargin=1*inch,
        leftMargin=1.5*inch,   # Standard screenplay left margin
        rightMargin=1*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Define screenplay styles
    title_style = ParagraphStyle(
        'ScreenplayTitle',
        parent=styles['Title'],
        fontName=font_family,
        fontSize=18,
        alignment=1,
        spaceAfter=24,
        leading=22
    )
    
    scene_heading_style = ParagraphStyle(
        'SceneHeading',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=0,
        spaceBefore=24,
        spaceAfter=12,
        leading=14
    )
    
    character_style = ParagraphStyle(
        'Character',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=0,
        leftIndent=2.2*inch,
        spaceBefore=12,
        spaceAfter=0,
        leading=14
    )
    
    parenthetical_style = ParagraphStyle(
        'Parenthetical',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=11,
        alignment=0,
        leftIndent=1.8*inch,
        rightIndent=2*inch,
        spaceBefore=0,
        spaceAfter=0,
        leading=13
    )
    
    dialog_style = ParagraphStyle(
        'Dialog',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=0,
        leftIndent=1*inch,
        rightIndent=1.5*inch,
        spaceBefore=0,
        spaceAfter=12,
        leading=16
    )
    
    action_style = ParagraphStyle(
        'Action',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=0,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=12,
        spaceAfter=12,
        leading=15
    )
    
    transition_style = ParagraphStyle(
        'Transition',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=2,  # Right
        spaceBefore=12,
        spaceAfter=24,
        leading=14
    )
    
    # Sample screenplay content
    story.append(Paragraph("VISUAL NOVEL SCREENPLAY", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Test Format - A4 Professional Layout", styles['Normal']))
    story.append(Spacer(1, 48))
    
    # Scene 1
    story.append(Paragraph("INT. COFFEE SHOP - DAY", scene_heading_style))
    story.append(Paragraph("ร้านกาแฟเล็กๆ ที่มีบรรยากาศอบอุ่น ลูกค้านั่งกินกาแฟและอ่านหนังสือ", action_style))
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("(มองไปที่นาฬิกา)", parenthetical_style))
    story.append(Paragraph("วันนี้อากาศดีจัง ขอกาแฟร้อนหนึ่งแก้วครับ", dialog_style))
    
    story.append(Paragraph("พนักงาน", character_style))
    story.append(Paragraph("รับทราบค่ะ กาแฟร้อนหนึ่งแก้ว", dialog_style))
    
    story.append(Paragraph("สมชายนั่งลงที่โต๊ะข้างหน้าต่าง มองออกไปข้างนอก", action_style))
    
    story.append(Paragraph("CUT TO:", transition_style))
    
    # Scene 2
    story.append(Paragraph("EXT. สวนสาธารณะ - บ่าย", scene_heading_style))
    story.append(Paragraph("สวนสาธารณะที่เต็มไปด้วยต้นไม้ใหญ่ เด็กๆ วิ่งเล่นอยู่", action_style))
    
    story.append(Paragraph("สมศรี", character_style))
    story.append(Paragraph("ที่นี่สวยจัง อากาศก็ดี", dialog_style))
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("(ยิ้ม)", parenthetical_style))
    story.append(Paragraph("ใช่แล้ว เราไปนั่งที่ม้านั่งโน้นกันไหม", dialog_style))
    
    story.append(Spacer(1, 24))
    story.append(Paragraph("FADE OUT.", transition_style))
    story.append(Spacer(1, 24))
    story.append(Paragraph("THE END", title_style))
    
    # Build PDF
    try:
        doc.build(story)
        file_size = os.path.getsize(test_pdf_path)
        print(f"✅ Screenplay format test PDF created: {file_size/1024:.1f} KB")
        print(f"📄 File: {test_pdf_path}")
        print("✅ Professional screenplay formatting applied:")
        print("   - A4 page size with proper margins")
        print("   - Scene headings (SLUG LINES)")
        print("   - Character names with correct indentation")
        print("   - Parentheticals formatting")
        print("   - Dialog with proper margins")
        print("   - Action lines full width")
        print("   - Transitions right-aligned")
        print("   - Thai font support")
        return True
        
    except Exception as e:
        print(f"❌ Error creating screenplay test: {e}")
        return False


if __name__ == "__main__":
    test_screenplay_formatting()
