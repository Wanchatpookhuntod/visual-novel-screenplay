#!/usr/bin/env python3
"""
ทดสอบ PDF ใหม่ด้วยวิธีที่รุนแรงกว่า
"""

import os
import time
import tempfile
import unicodedata

def fix_thai_text_advanced(text):
    """แก้ไขข้อความภาษาไทยด้วยวิธีที่รุนแรงกว่า"""
    if not text:
        return text
    
    # ใช้ Unicode normalization แบบ NFC
    text = unicodedata.normalize('NFC', text)
    
    # แทนที่คำที่มีปัญหาด้วยการใช้ HTML entities หรือ space
    problematic_words = {
        'ที่': 'ที่ ',  # เพิ่ม space หลังวรรณยุกต์
        'เพื่อ': 'เพื่อ ',
        'ก่อน': 'ก่อน ',
        'แล้ว': 'แล้ว ',
        'เดือน': 'เดือน ',
        'เขียน': 'เขียน ',
        'ใหม่': 'ใหม่ ',
        'ได้': 'ได้ ',
        'คืน': 'คืน ',
        'เมื่อ': 'เมื่อ ',
        'ปี่': 'ปี่ ',
        'กี่': 'กี่ '
    }
    
    # แทนที่คำที่มีปัญหา
    for problem_word, fixed_word in problematic_words.items():
        text = text.replace(problem_word, fixed_word)
    
    # วิธีการเพิ่มเติม: แทรก Zero Width Space (ZWSP) หลังวรรณยุกต์
    thai_tone_marks = ['\u0E48', '\u0E49', '\u0E4A', '\u0E4B']  # ่ ้ ๊ ๋
    thai_vowels = ['\u0E34', '\u0E35', '\u0E36', '\u0E37', '\u0E38', '\u0E39', '\u0E31']  # ิ ี ึ ื ุ ู ั
    
    result = ""
    for i, char in enumerate(text):
        result += char
        # เพิ่ม ZWSP หลังวรรณยุกต์
        if char in thai_tone_marks or char in thai_vowels:
            if i < len(text) - 1:  # ไม่ใช่ตัวสุดท้าย
                result += '\u200B'  # Zero Width Space
    
    return result

def test_ultimate_pdf():
    """ทดสอบ PDF แบบสุดโต่ง"""
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # ข้อความทดสอบ
        test_text = "ที่ เพื่อ ก่อน แล้ว เดือน เขียน ใหม่ ได้ คืน เมื่อ ปี่ กี่"
        
        # สร้าง PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = os.path.join(temp_dir, "ultimate_thai_test.pdf")
        
        print(f"🔄 กำลังสร้าง PDF แบบสุดโต่ง...")
        
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        
        story = []
        
        # ลองฟอนต์ต่างๆ
        font_options = [
            ('/System/Library/Fonts/Thonburi.ttc', 'Thonburi'),
            ('/System/Library/Fonts/Krungthep.ttc', 'Krungthep'),
            ('/Library/Fonts/Ayuthaya.ttf', 'Ayuthaya'),
        ]
        
        used_font = 'Helvetica'
        for font_path, font_name in font_options:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path, validate=True))
                    used_font = font_name
                    print(f"✅ ใช้ฟอนต์: {font_name}")
                    break
                except Exception as e:
                    print(f"❌ ไม่สามารถใช้ฟอนต์ {font_name}: {e}")
                    continue
        
        if used_font == 'Helvetica':
            print("⚠️  ใช้ฟอนต์ Helvetica (fallback)")
        
        # สร้าง styles แบบสุดโต่ง
        title_style = ParagraphStyle('Title',
                                   fontSize=18,
                                   fontName=used_font,
                                   alignment=TA_CENTER,
                                   spaceAfter=30,
                                   leading=30)  # leading มหาศาล
        
        extreme_style = ParagraphStyle('Extreme',
                                     fontSize=14,
                                     fontName=used_font,
                                     spaceAfter=20,
                                     leading=36)  # leading มหาศาล 36pt สำหรับ 14pt font
        
        # เพิ่มเนื้อหา
        story.append(Paragraph("ทดสอบ PDF แบบสุดโต่งสำหรับภาษาไทย", title_style))
        story.append(Paragraph(f"ฟอนต์ที่ใช้: {used_font}", extreme_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("1. ข้อความปกติ:", extreme_style))
        story.append(Paragraph(test_text, extreme_style))
        
        story.append(Paragraph("2. ข้อความที่แก้ไขแล้ว:", extreme_style))
        fixed_text = fix_thai_text_advanced(test_text)
        story.append(Paragraph(fixed_text, extreme_style))
        
        story.append(Paragraph("3. แยกเป็นคำๆ:", extreme_style))
        words = test_text.split()
        for word in words:
            fixed_word = fix_thai_text_advanced(word)
            story.append(Paragraph(f"• {word} → {fixed_word}", extreme_style))
        
        story.append(Paragraph("4. ทดสอบประโยคยาว:", extreme_style))
        long_sentence = "นี่คือประโยคที่มีคำที่มีปัญหาหลายคำ เช่น ที่ เพื่อ ก่อน แล้ว ซึ่งควรจะแสดงผลได้ดีขึ้น"
        fixed_long = fix_thai_text_advanced(long_sentence)
        story.append(Paragraph(fixed_long, extreme_style))
        
        # สร้าง PDF
        doc.build(story)
        
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            print(f"✅ สร้าง PDF สำเร็จ!")
            print(f"   ไฟล์: {pdf_filename}")
            print(f"   ขนาด: {file_size/1024:.1f} KB")
            print(f"   ฟอนต์: {used_font}")
            print(f"   Leading: 36pt (มหาศาล)")
            print(f"\n📖 เปิดไฟล์ PDF เพื่อตรวจสอบผลลัพธ์")
            print(f"🔍 ดูว่าวรรณยุกต์แสดงผลดีขึ้นหรือไม่")
        else:
            print("❌ ไม่สามารถสร้าง PDF ได้")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบ PDF แบบสุดโต่งสำหรับภาษาไทย")
    print("=" * 60)
    print()
    
    test_ultimate_pdf()
