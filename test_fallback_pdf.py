#!/usr/bin/env python3
"""
วิธีสุดท้าย: แทนที่คำที่มีปัญหาด้วยตัวอักษรที่แสดงผลได้
"""

import os
import time
import tempfile

def create_fallback_pdf():
    """สร้าง PDF โดยแทนที่คำที่มีปัญหาด้วยวิธีอื่น"""
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
        # แผนที่การแทนที่คำที่มีปัญหา
        word_replacements = {
            'ที่': 'ที่[นั่น]',     # เพิ่มคำอธิบาย
            'เพื่อ': 'เพื่อ[เพื่อให้]',
            'ก่อน': 'ก่อน[ก่อนหน้า]',
            'แล้ว': 'แล้ว[เสร็จแล้ว]',
            'เดือน': 'เดือน[เดือน]',
            'เขียน': 'เขียน[เขียน]',
            'ใหม่': 'ใหม่[ใหม่]',
            'ได้': 'ได้[สามารถ]',
            'คืน': 'คืน[กลับมา]',
            'เมื่อ': 'เมื่อ[เมื่อไหร่]',
            'ปี่': 'ปี่[เป่าปี่]',
            'กี่': 'กี่[จำนวน]'
        }
        
        # สร้าง PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = os.path.join(temp_dir, "fallback_thai_test.pdf")
        
        print(f"🔄 กำลังสร้าง PDF แบบ fallback...")
        
        doc = SimpleDocDocument(pdf_filename, pagesize=A4,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # สร้าง style ที่เน้นความชัดเจน
        clear_style = ParagraphStyle('Clear',
                                   fontSize=14,
                                   fontName='Helvetica',
                                   spaceAfter=15,
                                   leading=28)  # leading ขนาดใหญ่
        
        title_style = ParagraphStyle('Title',
                                   fontSize=18,
                                   fontName='Helvetica-Bold',
                                   alignment=TA_CENTER,
                                   spaceAfter=30,
                                   leading=30)
        
        # เพิ่มเนื้อหา
        story.append(Paragraph("วิธีแก้ปัญหาวรรณยุกต์แบบ Fallback", title_style))
        story.append(Paragraph(f"Generated: {time.strftime('%d %B %Y %H:%M น.')}", clear_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("1. คำต้นฉบับที่มีปัญหา:", clear_style))
        original_text = "ที่ เพื่อ ก่อน แล้ว เดือน เขียน ใหม่ ได้ คืน เมื่อ ปี่ กี่"
        story.append(Paragraph(original_text, clear_style))
        
        story.append(Paragraph("2. คำที่แทนที่ด้วย fallback:", clear_style))
        # แทนที่คำที่มีปัญหา
        fallback_text = original_text
        for problem_word, replacement in word_replacements.items():
            fallback_text = fallback_text.replace(problem_word, replacement)
        story.append(Paragraph(fallback_text, clear_style))
        
        story.append(Paragraph("3. แนวทางอื่น - ใช้ตัวเลขแทน:", clear_style))
        numbered_text = "1.ที่ 2.เพื่อ 3.ก่อน 4.แล้ว 5.เดือน 6.เขียน 7.ใหม่ 8.ได้ 9.คืน 10.เมื่อ 11.ปี่ 12.กี่"
        story.append(Paragraph(numbered_text, clear_style))
        
        story.append(Paragraph("4. แนวทางอื่น - เพิ่ม space:", clear_style))
        spaced_text = "ที่  เพื่อ  ก่อน  แล้ว  เดือน  เขียน  ใหม่  ได้  คืน  เมื่อ  ปี่  กี่"
        story.append(Paragraph(spaced_text, clear_style))
        
        story.append(Paragraph("5. แนวทางอื่น - ใช้วงเล็บ:", clear_style))
        bracket_text = "(ที่) (เพื่อ) (ก่อน) (แล้ว) (เดือน) (เขียน) (ใหม่) (ได้) (คืน) (เมื่อ) (ปี่) (กี่)"
        story.append(Paragraph(bracket_text, clear_style))
        
        story.append(Paragraph("6. ข้อเสนอแนะ:", clear_style))
        suggestion = """
        หากวรรณยุกต์ยังคงมีปัญหา แนะนำให้:
        • ใช้ฟอนต์อื่นที่รองรับภาษาไทยดีกว่า
        • ส่งออกเป็น Text แทน PDF
        • ใช้โปรแกรมอื่นในการสร้าง PDF
        • ปรับข้อความให้หลีกเลี่ยงคำที่มีปัญหา
        """
        story.append(Paragraph(suggestion, clear_style))
        
        # สร้าง PDF
        doc.build(story)
        
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            print(f"✅ สร้าง PDF fallback สำเร็จ!")
            print(f"   ไฟล์: {pdf_filename}")
            print(f"   ขนาด: {file_size/1024:.1f} KB")
            print(f"\n📋 ข้อเสนอแนะ:")
            print(f"   • หากวิธีนี้ยังไม่ได้ผล ปัญหาอาจอยู่ที่ฟอนต์หรือ ReportLab")
            print(f"   • ลองใช้ Text export แทน PDF")
            print(f"   • หรือใช้โปรแกรมอื่นสร้าง PDF")
        else:
            print("❌ ไม่สามารถสร้าง PDF ได้")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("วิธีแก้ปัญหาวรรณยุกต์แบบ Fallback")
    print("=" * 60)
    print()
    
    create_fallback_pdf()
