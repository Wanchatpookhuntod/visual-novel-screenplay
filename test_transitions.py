"""
Test Scene Transitions in Screenplay Format
Tests the separated IN and OUT transitions with proper positioning
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from font_manager import font_manager


def test_transition_formatting():
    """Test the new transition formatting with sample scenes"""
    print("Testing Scene Transition Formatting...")
    
    # Register fonts
    fonts_registered = font_manager.register_thai_fonts()
    font_family = font_manager.get_primary_thai_font()
    print(f"Using font: {font_family}")
    
    # Create test PDF
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'transition_test.pdf')
    
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
    
    # Transition IN style (left aligned)
    transition_in_style = ParagraphStyle(
        'TransitionIn',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=0,  # Left aligned
        spaceBefore=12,
        spaceAfter=12,
        leading=14
    )
    
    # Transition OUT style (right aligned)
    transition_out_style = ParagraphStyle(
        'TransitionOut',
        parent=styles['Normal'],
        fontName=font_family,
        fontSize=12,
        alignment=2,  # Right aligned
        spaceBefore=12,
        spaceAfter=24,
        leading=14
    )
    
    # Sample content with transitions
    story.append(Paragraph("TRANSITION TEST SCREENPLAY", title_style))
    story.append(Spacer(1, 48))
    
    # Scene 1 with FADE IN
    story.append(Paragraph("FADE IN:", transition_in_style))
    story.append(Paragraph("INT. COFFEE SHOP - DAY", scene_heading_style))
    story.append(Paragraph("ร้านกาแฟเล็กๆ ในย่านธุรกิจ ลูกค้าหลายคนนั่งทำงานด้วยแล็ปท็อป", action_style))
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("วันนี้อากาศดีจัง", dialog_style))
    
    story.append(Paragraph("CUT TO:", transition_out_style))
    
    # Scene 2 with different transition
    story.append(Paragraph("DISSOLVE IN:", transition_in_style))
    story.append(Paragraph("EXT. สวนสาธารณะ - บ่าย", scene_heading_style))
    story.append(Paragraph("สวนสาธารณะที่เขียวขจี มีเด็กๆ วิ่งเล่นอยู่", action_style))
    
    story.append(Paragraph("สมศรี", character_style))
    story.append(Paragraph("ที่นี่สวยมาก", dialog_style))
    
    story.append(Paragraph("FADE TO BLACK:", transition_out_style))
    
    # Scene 3 without IN transition
    story.append(Paragraph("INT. บ้าน - ค่ำ", scene_heading_style))
    story.append(Paragraph("บ้านเล็กๆ ที่อบอุ่น มีแสงไฟส้มนวลตา", action_style))
    
    story.append(Paragraph("สมชาย", character_style))
    story.append(Paragraph("กลับบ้านแล้ว", dialog_style))
    
    # Final transition
    story.append(Spacer(1, 24))
    story.append(Paragraph("FADE OUT.", transition_out_style))
    story.append(Spacer(1, 24))
    story.append(Paragraph("THE END", title_style))
    
    # Build PDF
    try:
        doc.build(story)
        file_size = os.path.getsize(test_pdf_path)
        print(f"✅ Transition test PDF created: {file_size/1024:.1f} KB")
        print(f"📄 File: {test_pdf_path}")
        print("✅ Transition formatting applied:")
        print("   - IN transitions before scene heading (left aligned)")
        print("   - OUT transitions after scene content (right aligned)")
        print("   - FADE IN, DISSOLVE IN, CUT TO, FADE OUT tested")
        print("   - Proper spacing and positioning")
        return True
        
    except Exception as e:
        print(f"❌ Error creating transition test: {e}")
        return False


if __name__ == "__main__":
    test_transition_formatting()
