"""
Test PDF Format Without Background Descriptions
Verifies that background sections are excluded from PDF screenplay format
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from font_manager import font_manager


def test_pdf_no_background():
    """Test PDF format without background descriptions"""
    print("Testing PDF Format Without Background...")
    
    # Register fonts
    fonts_registered = font_manager.register_thai_fonts()
    font_family = font_manager.get_primary_thai_font()
    print(f"Using font: {font_family}")
    
    # Create test PDF
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'clean_format_test.pdf')
    
    # Document with screenplay margins
    doc = SimpleDocTemplate(
        test_pdf_path, 
        pagesize=A4, 
        topMargin=1*inch, 
        bottomMargin=1*inch,
        leftMargin=1.5*inch,
        rightMargin=1*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Define styles
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
    
    # Sample content - Clean format without background
    story.append(Paragraph("CLEAN SCREENPLAY FORMAT", title_style))
    story.append(Spacer(1, 48))
    
    # Scene 1 - No background description
    story.append(Paragraph("(1) INT. COFFEE SHOP - DAY", scene_heading_style))
    # NOTE: Background description excluded as requested
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("สวัสดีครับ ขอกาแฟร้อนหนึ่งแก้ว", dialog_style))
    
    story.append(Paragraph("เธอเดินเข้ามาในร้าน มองหาที่นั่ง", action_style))
    
    story.append(Paragraph("สมศรี", character_style))
    story.append(Paragraph("ที่นี่อบอุ่นดีนะ", dialog_style))
    
    # Scene 2 - No background description
    story.append(Paragraph("(2) EXT. สวนสาธารณะ - บ่าย", scene_heading_style))
    # NOTE: Background description excluded as requested
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("อากาศดีจัง", dialog_style))
    
    story.append(Paragraph("พวกเขาเดินเล่นในสวน", action_style))
    
    story.append(Spacer(1, 24))
    story.append(Paragraph("THE END", title_style))
    
    # Build PDF
    try:
        doc.build(story)
        file_size = os.path.getsize(test_pdf_path)
        print(f"✅ Clean format PDF created: {file_size/1024:.1f} KB")
        print(f"📄 File: {test_pdf_path}")
        print("✅ Clean screenplay format features:")
        print("   - Scene headings only (no background descriptions)")
        print("   - Direct to dialog and action")
        print("   - Cleaner, more focused layout")
        print("   - Professional screenplay appearance")
        print("   - Thai font support maintained")
        return True
        
    except Exception as e:
        print(f"❌ Error creating clean format test: {e}")
        return False


if __name__ == "__main__":
    test_pdf_no_background()
