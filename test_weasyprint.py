#!/usr/bin/env python3
"""
ทดสอบ WeasyPrint สำหรับภาษาไทย
"""

import os
import time
import tempfile

def test_weasyprint_thai():
    """ทดสอบ WeasyPrint กับข้อความภาษาไทยที่มีปัญหาวรรณยุกต์"""
    
    try:
        from weasyprint import HTML, CSS
        
        # ข้อความทดสอบที่มีปัญหาวรรณยุกต์
        test_text = "ที่ เพื่อ ก่อน แล้ว เดือน เขียน ใหม่ ได้ คืน เมื่อ ปี่ กี่"
        
        # Get the path to Sarabun fonts
        sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
        sarabun_regular = os.path.join(sarabun_path, 'Sarabun-Regular.ttf')
        sarabun_bold = os.path.join(sarabun_path, 'Sarabun-Bold.ttf')
        
        print(f"🔍 ตรวจสอบฟอนต์:")
        print(f"   Sarabun Regular: {'✅ พบ' if os.path.exists(sarabun_regular) else '❌ ไม่พบ'} {sarabun_regular}")
        print(f"   Sarabun Bold: {'✅ พบ' if os.path.exists(sarabun_bold) else '❌ ไม่พบ'} {sarabun_bold}")
        
        # CSS สำหรับฟอนต์ไทย
        css_content = f"""
        @font-face {{
            font-family: 'Sarabun';
            src: url('file://{sarabun_regular}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Sarabun';
            src: url('file://{sarabun_bold}') format('truetype');
            font-weight: bold;
            font-style: normal;
        }}
        
        @page {{
            size: A4;
            margin: 1in;
        }}
        
        body {{
            font-family: 'Sarabun', Arial, sans-serif;
            font-size: 14pt;
            line-height: 1.6;
            color: black;
        }}
        
        .title {{
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 30pt;
            color: #333;
        }}
        
        .test-section {{
            margin-bottom: 20pt;
            padding: 10pt;
            border: 1pt solid #ddd;
        }}
        
        .test-title {{
            font-weight: bold;
            font-size: 16pt;
            margin-bottom: 10pt;
            color: #666;
        }}
        
        .normal-text {{
            font-size: 14pt;
            margin-bottom: 10pt;
        }}
        
        .large-text {{
            font-size: 18pt;
            margin-bottom: 10pt;
        }}
        
        .bold-text {{
            font-weight: bold;
            margin-bottom: 10pt;
        }}
        """
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WeasyPrint Thai Test</title>
        </head>
        <body>
            <div class="title">ทดสอบ WeasyPrint กับภาษาไทย</div>
            <p style="text-align: center; margin-bottom: 30pt;">Generated: {time.strftime('%d %B %Y เวลา %H:%M น.')}</p>
            
            <div class="test-section">
                <div class="test-title">1. ข้อความทดสอบพื้นฐาน</div>
                <div class="normal-text">สวัสดีครับ นี่คือการทดสอบภาษาไทยใน WeasyPrint</div>
                <div class="normal-text">ตัวอักษรไทยควรจะแสดงได้ถูกต้อง</div>
            </div>
            
            <div class="test-section">
                <div class="test-title">2. ข้อความที่มีปัญหาวรรณยุกต์</div>
                <div class="normal-text">คำที่มักมีปัญหา: {test_text}</div>
                <div class="large-text">ขนาดใหญ่: {test_text}</div>
                <div class="bold-text">ตัวหนา: {test_text}</div>
            </div>
            
            <div class="test-section">
                <div class="test-title">3. ประโยคยาว</div>
                <div class="normal-text">
                    ในช่วงเวลาที่ผ่านมานี้ เราได้พยายามแก้ไขปัญหาการแสดงผลวรรณยุกต์ภาษาไทยใน PDF 
                    โดยเฉพาะคำที่มีสระและวรรณยุกต์ เช่น "ที่" "เพื่อ" "ก่อน" และ "แล้ว" 
                    ซึ่งมักจะมีปัญหาวรรณยุกต์ลอยหรือจมลงไป
                </div>
            </div>
            
            <div class="test-section">
                <div class="test-title">4. บทสนทนาตัวอย่าง</div>
                <div style="text-align: center; font-weight: bold; margin: 10pt 0;">ตัวละคร A</div>
                <div style="margin-left: 1in; margin-right: 0.5in;">
                    "สวัสดีครับ ผมมาที่นี่เพื่อทดสอบการแสดงผลตัวอักษรไทย"
                </div>
                
                <div style="text-align: center; font-weight: bold; margin: 10pt 0;">ตัวละคร B</div>
                <div style="margin-left: 1in; margin-right: 0.5in;">
                    "ดีมากเลยครับ วรรณยุกต์ในคำ 'ที่' และ 'เพื่อ' แสดงผลได้ถูกต้องแล้วหรือยัง?"
                </div>
            </div>
            
            <div class="test-section">
                <div class="test-title">5. สัญลักษณ์และตัวเลข</div>
                <div class="normal-text">
                    วันที่: {time.strftime('%d/%m/%Y')} เวลา: {time.strftime('%H:%M น.')}
                </div>
                <div class="normal-text">
                    ราคา: ฿1,234.56 | อุณหภูมิ: 25°C | เปอร์เซ็นต์: 95%
                </div>
            </div>
        </body>
        </html>
        """
        
        # สร้าง PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = os.path.join(temp_dir, "weasyprint_thai_test.pdf")
        
        print(f"\n🔄 กำลังสร้าง PDF...")
        
        # สร้าง HTML และ CSS objects
        html_doc = HTML(string=html_content, base_url='.')
        css_doc = CSS(string=css_content)
        
        # สร้าง PDF
        html_doc.write_pdf(pdf_filename, stylesheets=[css_doc])
        
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            print(f"✅ สร้าง PDF สำเร็จ!")
            print(f"   ไฟล์: {pdf_filename}")
            print(f"   ขนาด: {file_size/1024:.1f} KB")
            print(f"\n📖 เปิดไฟล์ PDF เพื่อตรวจสอบ:")
            print(f"   • วรรณยุกต์ในคำ 'ที่' แสดงผลถูกต้องหรือไม่")
            print(f"   • วรรณยุกต์ในคำ 'เพื่อ' แสดงผลถูกต้องหรือไม่")
            print(f"   • วรรณยุกต์ในคำอื่นๆ แสดงผลถูกต้องหรือไม่")
            print(f"\n🎯 หาก WeasyPrint แสดงผลได้ดีแล้ว จะใช้ในโปรเจกต์หลัก")
        else:
            print("❌ ไม่สามารถสร้าง PDF ได้")
            
    except ImportError as e:
        print(f"❌ ไม่สามารถ import WeasyPrint ได้: {e}")
        print("💡 ติดตั้งด้วย: pip install weasyprint")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("ทดสอบ WeasyPrint สำหรับภาษาไทย")
    print("=" * 60)
    print()
    
    test_weasyprint_thai()
