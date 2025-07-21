# Visual Novel Node Editor

## 🚀 พร้อมใช้งานเต็มประสิทธิภาพ!

**Visual Novel Node Editor** เป็นเครื่องมือสำหรับสร้าง screenplay สำหรับ visual novel ด้วยระบบ node-based ที่ใช้งานง่าย รองรับภาษาไทยครบถ้วน และส่งออก PDF แบบมืออาชีพ

### ✅ สิ่งที่ได้เมื่อใช้งาน
- 📝 **สร้าง screenplay ได้ทันที** - ไม่ต้องเรียนรู้ซับซ้อน
- 🎨 **ฟอนต์ไทยสวยงาม** - THSarabunNew ในทุก export
- 📄 **PDF มาตรฐานสากล** - รูปแบบ screenplay แบบ Hollywood
- 🔗 **ระบบ node ที่เข้าใจง่าย** - ลากเชื่อมได้ทันที
- 💾 **บันทึก/โหลดไฟล์** - ทำงานต่อได้ตลอดเวลา

## 🎯 เริ่มใช้งานภายใน 30 วินาที

### 1. รันโปรแกรม
```bash
python main_clean.py
```

### 2. สร้าง node แรก
- **Right-click** พื้นที่ว่าง → เลือก "Create Start Node" หรือ "Create Scene Node"

### 3. แก้ไขเนื้อหา
- **Double-click** node → เพิ่มบทสนทนาและ action

### 4. เชื่อมต่อ story
- **Drag** จากวงกลมสีเขียว (output) ไปยังวงกลมสีแดง (input)

### 5. ส่งออก screenplay
- **File → Export → PDF Screenplay** → ได้ไฟล์ PDF พร้อมใช้!

## โครงสร้างไฟล์ใหม่ (แยกเป็นระเบียบ)

### ไฟล์หลัก
- **`main_clean.py`** - จุดเริ่มต้นของโปรแกรม (entry point) พร้อม font initialization
- **`main_window.py`** - คลาส MainWindow และ UI หลัก
- **`graphics_items.py`** - คลาสทั้งหมดที่เกี่ยวกับ graphics (NodeScene, StartNode, EdgeGraphicsItem, InputOutputCircle)
- **`views.py`** - คลาส NodeGraphicsView สำหรับการแสดงผลและการควบคุม
- **`export_manager.py`** - จัดการการ export ทุกรูปแบบ (Text, JSON, CSV, PDF) รองรับ ReportLab เท่านั้น
- **`font_manager.py`** - ระบบจัดการฟอนต์ไทย THSarabunNew อัตโนมัติ

### ไฟล์ระบบฟอนต์
- **`font/`** - โฟลเดอร์ฟอนต์ไทย THSarabunNew (4 variants)
  - `THSarabunNew.ttf` - ปกติ
  - `THSarabunNew Bold.ttf` - หนา
  - `THSarabunNew Italic.ttf` - เอียง
  - `THSarabunNew BoldItalic.ttf` - หนาเอียง

### ไฟล์เดิม (ยังคงอยู่)
- **`main.py`** - ไฟล์เดิมที่มีฟีเจอร์ครบ (รวมทุกอย่างไว้ในไฟล์เดียว)
- **`form.py`** - ฟอร์มสำหรับแก้ไขข้อมูล node

## วิธีการใช้งาน

### รันโปรแกรมแบบใหม่ (แยกไฟล์) - แนะนำ ⭐
```bash
python main_clean.py
```

### รันโปรแกรมแบบเดิม
```bash
# เวอร์ชันปัจจุบัน (มีฟีเจอร์ครบ)
python main.py
```

## 📊 สรุปไฟล์ในโปรเจค

| ไฟล์ | วัตถุประสงค์ | สถานะ | ความสำคัญ |
|------|------------|--------|------------|
| `main_clean.py` | **รันโปรแกรมหลัก** | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `export_manager.py` | ส่งออก PDF/Text/JSON/CSV | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `font_manager.py` | จัดการฟอนต์ไทยอัตโนมัติ | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `main_window.py` | หน้าต่างหลักของโปรแกรม | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `graphics_items.py` | ระบบ node และ graphics | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `views.py` | การแสดงผลและควบคุม | ✅ พร้อมใช้ | ⭐⭐⭐ **จำเป็น** |
| `form.py` | ฟอร์มแก้ไข node | ✅ พร้อมใช้ | ⭐⭐ สำคัญ |
| `font/` | โฟลเดอร์ฟอนต์ไทย | ✅ พร้อมใช้ | ⭐⭐ สำคัญ |
| `main.py` | ไฟล์เดิม (สำรอง) | ✅ ใช้ได้ | ⭐ สำรอง |

### 🎯 ไฟล์สำคัญที่ต้องมี
1. **`main_clean.py`** - เริ่มต้นโปรแกรม
2. **`font/THSarabunNew*.ttf`** - ฟอนต์ไทย (4 ไฟล์)
3. **`requirements.txt`** - dependencies ที่ต้องติดตั้ง

## ข้อดีของการแยกไฟล์

1. **อ่านง่าย** - แต่ละไฟล์มีหน้าที่ชัดเจน
2. **แก้ไขง่าย** - หาส่วนที่ต้องการแก้ไขได้รวดเร็ว
3. **ดูแลรักษา** - แก้ไขส่วนหนึ่งไม่กระทบส่วนอื่น
4. **ขยายฟีเจอร์** - เพิ่มฟีเจอร์ใหม่ได้ง่าย
5. **ทดสอบ** - ทดสอบแต่ละส่วนแยกกันได้

## ฟีเจอร์ทั้งหมด

### ✨ ฟีเจอร์หลัก
- สร้าง/แก้ไข/ลบ node
- เชื่อมต่อ node ด้วย edge
- บันทึก/โหลดไฟล์ JSON
- Export เป็น Text, JSON, CSV, PDF
- ซูมอิน/ซูมเอาท์
- แก้ไขข้อมูล dialog และ action

### 🎨 ระบบฟอนต์ไทย (ใหม่!)
- **THSarabunNew Font System** - ฟอนต์ไทยมืออาชีพ
- **Auto Font Registration** - ลงทะเบียนฟอนต์อัตโนมัติ
- **4 Font Variants** - ปกติ, หนา, เอียง, หนาเอียง
- **Thai Text Optimization** - รองรับวรรณยุกต์และสระไทยครบถ้วน
- **Unicode Normalization** - แสดงผลข้อความไทยถูกต้อง

### 📄 PDF Export มืออาชีพ (ปรับปรุงใหม่!)
- **A4 Screenplay Format** - รูปแบบ screenplay มาตรฐานสากล
- **Professional Margins** - ขอบกระดาษตามมาตรฐานอุตสาหกรรม
- **Scene Transitions** - IN transitions (ซ้าย), OUT transitions (ขวา)
- **Character Indentation** - การเยื้องชื่อตัวละครมาตรฐาน
- **Dialog Formatting** - รูปแบบบทสนทนาแบบมืออาชีพ
- **Clean Layout** - ไม่รวม background descriptions (เน้นความกระชับ)
- **ReportLab Only** - ไม่ต้องติดตั้ง GTK หรือ WeasyPrint

### 🔧 เทคนิคขั้นสูง
- **Font Manager System** - ระบบจัดการฟอนต์แบบ modular
- **Automatic Dependencies** - ตรวจสอบและติดตั้ง dependencies อัตโนมัติ
- **Error Handling** - จัดการข้อผิดพลาดอย่างสมบูรณ์
- **Cross-Platform** - ทำงานได้ทั้ง Windows, Mac, Linux

## 💻 ข้อกำหนดระบบ (เรียบง่าย)

### สิ่งที่ต้องมี
- **Python 3.8+** 
- **PySide6** (GUI framework)
- **ReportLab** (PDF generation)

### ติดตั้งแบบอัตโนมัติ (แนะนำ) ⭐

#### Windows
```batch
install.bat
```

#### macOS/Linux
```bash
chmod +x install.sh
./install.sh
```

### ติดตั้งด้วยตนเอง
```bash
# ติดตั้งจาก requirements.txt
pip install -r requirements.txt
```

หรือติดตั้งแยก:
```bash
pip install PySide6 reportlab pillow
```

### ตรวจสอบการติดตั้ง
```bash
python -c "import PySide6, reportlab, PIL; print('✓ All dependencies ready!')"
```

## 🎮 วิธีใช้งานแบบละเอียด

### การสร้าง Node
1. **Right-click** พื้นที่ว่าง
2. เลือก **"Create Start Node"** (node เริ่มต้น) หรือ **"Create Scene Node"** (ฉากทั่วไป)
3. Node จะปรากฏขึ้นพร้อมใช้งาน

### การแก้ไขเนื้อหา
1. **Double-click** node ที่ต้องการแก้ไข
2. กรอกข้อมูล:
   - **Scene Type**: INT./EXT.
   - **Location**: สถานที่
   - **Time**: เวลา
   - **Dialog**: บทสนทนา (character + text)
   - **Action**: การกระทำ/คำบรรยาย
3. กด **"Save"** เสร็จสิ้น

### การเชื่อมต่อ Story
1. **Drag** จากวงกลมสีเขียว (output) ของ node แรก
2. ไปยังวงกลมสีแดง (input) ของ node ถัดไป
3. เส้นเชื่อมจะปรากฏขึ้น = story flow พร้อม

### การส่งออกไฟล์
- **Text**: File → Export → Text Screenplay
- **JSON**: File → Export → JSON Data  
- **CSV**: File → Export → CSV Data
- **PDF**: File → Export → PDF Screenplay ⭐ **แนะนำ**

### การควบคุมมุมมอง
- **Mouse Wheel**: ซูมอิน/เอาท์
- **Middle-click + Drag**: เลื่อนมุมมอง
- **Ctrl + Mouse Wheel**: ซูมแม่นยำ

## 🛠️ แก้ปัญหาเบื้องต้น

### ปัญหาที่พบบ่อย
**Q: โปรแกรมไม่เปิด**
- A: ตรวจสอบว่าติดตั้ง Python 3.8+ และ dependencies ครบแล้ว

**Q: ฟอนต์ไทยไม่แสดงใน PDF**
- A: ฟอนต์ THSarabunNew จะโหลดอัตโนมัติจากโฟลเดอร์ `font/`

**Q: PDF ไม่สามารถสร้างได้**
- A: ตรวจสอบว่าติดตั้ง `reportlab` แล้ว: `pip install reportlab`

**Q: Node เชื่อมต่อไม่ได้**
- A: ต้อง drag จากวงกลมเขียว (output) ไปวงกลมแดง (input) เท่านั้น

### 💡 เทคนิคการใช้งาน
- **บันทึกบ่อยๆ**: File → Save Project เพื่อไม่สูญหายข้อมูล
- **ตั้งชื่อ node ให้ชัดเจน**: จะได้หาง่ายเมื่อ project ใหญ่
- **ใช้ scene transitions**: เพิ่ม FADE IN, CUT TO เพื่อความเป็นมืออาชีพ
- **ตรวจสอบ connection**: ก่อน export ให้แน่ใจว่า node เชื่อมต่อถูกต้อง

## 📚 เอกสารเพิ่มเติม

- **`FONT_SYSTEM.md`** - รายละเอียดระบบฟอนต์ไทย
- **`SCREENPLAY_FORMAT_A4.md`** - มาตรฐานการจัดรูปแบบ screenplay
- **`requirements.txt`** - รายการ dependencies ที่จำเป็น

## 🎉 พร้อมสร้างสรรค์แล้ว!

เริ่มสร้าง visual novel screenplay ของคุณได้เลย ระบบพร้อมใช้งานครบทุกฟีเจอร์!

---
