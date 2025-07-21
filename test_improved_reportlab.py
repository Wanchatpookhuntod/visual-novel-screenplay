#!/usr/bin/env python3
"""
ทดสอบ ReportLab ที่ปรับปรุงแล้วสำหรับภาษาไทย
"""

import os
import time
import tempfile
import unicodedata

def normalize_thai_text(text):
    """ปรับปรุงข้อความภาษาไทยเพื่อแสดงผลวรรณยุกต์ได้ถูกต้อง"""
    if not text:
        return text
    
    # ใช้ Unicode normalization แบบ NFC
    text = unicodedata.normalize('NFC', text)
    
    # รายการวรรณยุกต์ภาษาไทย
    thai_vowels = [
        '\u0E31',  # ั mai han-akat
        '\u0E34',  # ิ sara i
        '\u0E35',  # ี sara ii
        '\u0E36',  # ึ sara ue
        '\u0E37',  # ื sara uee
        '\u0E38',  # ุ sara u
        '\u0E39',  # ู sara uu
        '\u0E3A',  # ฺ phinthu
    ]
    
    thai_tone_marks = [
        '\u0E48',  # ่ mai ek
        '\u0E49',  # ้ mai tho
        '\u0E4A',  # ๊ mai tri
        '\u0E4B',  # ๋ mai chattawa
        '\u0E4C',  # ์ thanthakhat
    ]
    
    # แทรก Zero Width Non-Joiner (ZWNJ) ก่อนวรรณยุกต์เพื่อป้องกันการรวมตัว
    result = ""
    for i, char in enumerate(text):
        if char in thai_vowels or char in thai_tone_marks:
            # เช็คว่าตัวก่อนหน้าไม่ใช่ ZWNJ แล้ว
            if i > 0 and text[i-1] != '\u200C':
                result += '\u200C'  # ZWNJ
        result += char
    
    return result

def test_improved_reportlab():
    """ทดสอบ ReportLab ที่ปรับปรุงแล้วกับข้อความภาษาไทยที่มีปัญหาวรรณยุกต์"""
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        
        # ข้อความทดสอบที่มีปัญหาวรรณยุกต์
        test_text = "ที่ เพื่อ ก่อน แล้ว เดือน เขียน ใหม่ ได้ คืน เมื่อ ปี่ กี่"
        
        # Get the path to Sarabun fonts
        sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
        sarabun_regular = os.path.join(sarabun_path, 'Sarabun-Regular.ttf')
        sarabun_bold = os.path.join(sarabun_path, 'Sarabun-Bold.ttf')
        
        print(f"🔍 ตรวจสอบฟอนต์:")
        print(f"   Sarabun Regular: {'✅ พบ' if os.path.exists(sarabun_regular) else '❌ ไม่พบ'} {sarabun_regular}")
        print(f"   Sarabun Bold: {'✅ พบ' if os.path.exists(sarabun_bold) else '❌ ไม่พบ'} {sarabun_bold}")
        
        # สร้าง PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = os.path.join(temp_dir, "improved_reportlab_thai_test.pdf")
        
        print(f"\n🔄 กำลังสร้าง PDF...")
        
        # สร้าง PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        
        story = []
        
        # ลงทะเบียนฟอนต์ไทยพร้อมการตั้งค่าที่ปรับปรุงแล้ว
        try:
            pdfmetrics.registerFont(TTFont('Sarabun', sarabun_regular, validate=True, subfontIndex=0))
            pdfmetrics.registerFont(TTFont('Sarabun-Bold', sarabun_bold, validate=True, subfontIndex=0))
            
            registerFontFamily('Sarabun', normal='Sarabun', bold='Sarabun-Bold')
            
            thai_font = 'Sarabun'
            thai_font_bold = 'Sarabun-Bold'
            print("✅ ลงทะเบียนฟอนต์ไทยสำเร็จ")
        except Exception as e:
            print(f"❌ ไม่สามารถลงทะเบียนฟอนต์ไทยได้: {e}")
            thai_font = 'Helvetica'
            thai_font_bold = 'Helvetica-Bold'
        
        # สร้าง styles พร้อม leading ที่เพิ่มขึ้น
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title',
                                   fontSize=18,
                                   fontName=thai_font_bold,
                                   alignment=TA_CENTER,
                                   spaceAfter=30,
                                   leading=22)
        
        heading_style = ParagraphStyle('Heading',
                                     fontSize=14,
                                     fontName=thai_font_bold,
                                     spaceAfter=10,
                                     spaceBefore=20,
                                     leading=18)
        
        normal_style = ParagraphStyle('Normal',
                                    fontSize=12,
                                    fontName=thai_font,
                                    spaceAfter=10,
                                    leading=18)  # เพิ่ม leading สำหรับวรรณยุกต์
        
        large_style = ParagraphStyle('Large',
                                   fontSize=16,
                                   fontName=thai_font,
                                   spaceAfter=10,
                                   leading=22)
        
        bold_style = ParagraphStyle('Bold',
                                  fontSize=12,
                                  fontName=thai_font_bold,
                                  spaceAfter=10,
                                  leading=18)
        
        # เพิ่มเนื้อหา
        story.append(Paragraph("ทดสอบ ReportLab ที่ปรับปรุงแล้วสำหรับภาษาไทย", title_style))
        story.append(Paragraph(f"Generated: {time.strftime('%d %B %Y เวลา %H:%M น.')}", normal_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("1. ข้อความทดสอบพื้นฐาน", heading_style))
        story.append(Paragraph("สวัสดีครับ นี่คือการทดสอบภาษาไทยใน ReportLab ที่ปรับปรุงแล้ว", normal_style))
        story.append(Paragraph("ตัวอักษรไทยควรจะแสดงได้ถูกต้อง", normal_style))
        
        story.append(Paragraph("2. ข้อความที่มีปัญหาวรรณยุกต์ (ก่อนปรับปรุง)", heading_style))
        story.append(Paragraph(f"คำที่มักมีปัญหา: {test_text}", normal_style))
        story.append(Paragraph(f"ขนาดใหญ่: {test_text}", large_style))
        story.append(Paragraph(f"ตัวหนา: {test_text}", bold_style))
        
        story.append(Paragraph("3. ข้อความที่มีปัญหาวรรณยุกต์ (หลังปรับปรุง)", heading_style))
        normalized_text = normalize_thai_text(test_text)
        story.append(Paragraph(f"คำที่ปรับปรุงแล้ว: {normalized_text}", normal_style))
        story.append(Paragraph(f"ขนาดใหญ่: {normalized_text}", large_style))
        story.append(Paragraph(f"ตัวหนา: {normalized_text}", bold_style))
        
        story.append(Paragraph("4. ประโยคยาว", heading_style))
        long_sentence = normalize_thai_text(
            "ในช่วงเวลาที่ผ่านมานี้ เราได้พยายามแก้ไขปัญหาการแสดงผลวรรณยุกต์ภาษาไทยใน PDF "
            "โดยเฉพาะคำที่มีสระและวรรณยุกต์ เช่น \"ที่\" \"เพื่อ\" \"ก่อน\" และ \"แล้ว\" "
            "ซึ่งมักจะมีปัญหาวรรณยุกต์ลอยหรือจมลงไป"
        )
        story.append(Paragraph(long_sentence, normal_style))
        
        story.append(Paragraph("5. บทสนทนาตัวอย่าง", heading_style))
        
        # Character style สำหรับบทสนทนา
        character_style = ParagraphStyle('Character',
                                       fontSize=12,
                                       fontName=thai_font_bold,
                                       alignment=TA_CENTER,
                                       spaceBefore=10,
                                       spaceAfter=5,
                                       leading=16)
        
        dialog_style = ParagraphStyle('Dialog',
                                    fontSize=12,
                                    fontName=thai_font,
                                    leftIndent=1*inch,
                                    rightIndent=0.5*inch,
                                    spaceAfter=10,
                                    leading=18)
        
        story.append(Paragraph("ตัวละคร A", character_style))
        story.append(Paragraph(normalize_thai_text(
            "\"สวัสดีครับ ผมมาที่นี่เพื่อทดสอบการแสดงผลตัวอักษรไทย\""
        ), dialog_style))
        
        story.append(Paragraph("ตัวละคร B", character_style))
        story.append(Paragraph(normalize_thai_text(
            "\"ดีมากเลยครับ วรรณยุกต์ในคำ 'ที่' และ 'เพื่อ' แสดงผลได้ถูกต้องแล้วหรือยัง?\""
        ), dialog_style))
        
        story.append(Paragraph("6. สรุปผล", heading_style))
        story.append(Paragraph(normalize_thai_text(
            "การปรับปรุงนี้ใช้ Unicode normalization (NFC) และ Zero Width Non-Joiner (ZWNJ) "
            "เพื่อป้องกันการรวมตัวของวรรณยุกต์ที่ไม่ถูกต้อง"
        ), normal_style))
        
        # สร้าง PDF
        doc.build(story)
        
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            print(f"✅ สร้าง PDF สำเร็จ!")
            print(f"   ไฟล์: {pdf_filename}")
            print(f"   ขนาด: {file_size/1024:.1f} KB")
            print(f"\n📖 เปิดไฟล์ PDF เพื่อเปรียบเทียบ:")
            print(f"   • เปรียบเทียบ section 2 (ก่อนปรับปรุง) กับ section 3 (หลังปรับปรุง)")
            print(f"   • ตรวจสอบว่าวรรณยุกต์ใน section 3 แสดงผลได้ดีกว่าหรือไม่")
            print(f"\n🎯 หากผลลัพธ์ดี จะใช้วิธีนี้ในโปรเจกต์หลัก")
        else:
            print("❌ ไม่สามารถสร้าง PDF ได้")
            
    except ImportError as e:
        print(f"❌ ไม่สามารถ import ReportLab ได้: {e}")
        print("💡 ติดตั้งด้วย: pip install reportlab")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบ ReportLab ที่ปรับปรุงแล้วสำหรับภาษาไทย")
    print("=" * 60)
    print()
    
    test_improved_reportlab()
