# Visual Novel Node Editor - การสร้างไฟล์ .exe

## ขั้นตอนการสร้าง .exe

### วิธีที่ 1: ใช้สคริปต์อัตโนมัติ (แนะนำ)

1. **เปิด Command Prompt หรือ PowerShell**
2. **ไปยังโฟลเดอร์โปรเจค**
   ```cmd
   cd "d:\CodePython\visual-novel-screenplay"
   ```
3. **รันสคริปต์ build**
   ```cmd
   build_exe.bat
   ```
4. **รอให้เสร็จ** (ประมาณ 2-5 นาที)
5. **ไฟล์ .exe จะอยู่ในโฟลเดอร์ `dist/`**

### วิธีที่ 2: ทำเองทีละขั้นตอน

1. **ติดตั้ง PyInstaller**
   ```cmd
   pip install pyinstaller
   ```

2. **สร้าง .exe**
   ```cmd
   pyinstaller build_exe.spec
   ```

3. **ไฟล์ .exe จะอยู่ใน `dist/Visual_Novel_Editor.exe`**

## ผลลัพธ์

### ไฟล์ที่ได้
- **`dist/Visual_Novel_Editor.exe`** - โปรแกรมพร้อมใช้งาน
- **ขนาด**: ประมาณ 80-150 MB
- **การใช้งาน**: Double-click เพื่อเปิดโปรแกรม

### สิ่งที่รวมอยู่ใน .exe
- ✅ โปรแกรม Visual Novel Node Editor ครบทุกฟีเจอร์
- ✅ ฟอนต์ไทย THSarabunNew (4 แบบ)
- ✅ PySide6 (GUI framework)
- ✅ ReportLab (PDF export)
- ✅ Pillow (image processing)
- ✅ Python runtime (ไม่ต้องติดตั้ง Python บนเครื่องอื่น)

## การแจกจ่าย

### สำหรับผู้ใช้ทั่วไป
1. **Copy ไฟล์ `Visual_Novel_Editor.exe`** ไปยังเครื่องอื่น
2. **Double-click เพื่อรัน** - ไม่ต้องติดตั้งอะไรเพิ่ม
3. **ใช้งานได้ทันที** - สร้าง screenplay และ export PDF

### สำหรับการพัฒนาต่อ
- **แก้ไขโค้ด** → **รัน `build_exe.bat` ใหม่** → **ได้ .exe เวอร์ชันใหม่**

## แก้ปัญหา

### ปัญหาที่อาจพบ
**Q: .exe ใหญ่เกินไป**
- A: ปกติแล้ว PyInstaller จะรวมทุกอย่างไว้ ทำให้ขนาดใหญ่ แต่ใช้งานสะดวก

**Q: .exe เปิดไม่ได้**
- A: ลองเปิด Command Prompt แล้วรัน .exe เพื่อดู error message

**Q: Missing module error**
- A: เพิ่ม module ที่หายไปใน `hiddenimports` ในไฟล์ `build_exe.spec`

**Q: ฟอนต์ไทยไม่แสดง**
- A: ตรวจสอบว่าฟอนต์ในโฟลเดอร์ `font/` ถูกรวมเข้า .exe แล้ว

## เทคนิคขั้นสูง

### ลดขนาดไฟล์
1. แก้ไข `build_exe.spec`:
   ```python
   excludes=['tkinter', 'matplotlib', 'numpy', 'scipy']
   ```

2. เพิ่ม UPX compression:
   ```python
   upx=True
   ```

### เพิ่มไอคอน
1. เตรียมไฟล์ `.ico`
2. แก้ไข `build_exe.spec`:
   ```python
   icon='icon.ico'
   ```

### Build แบบ One-Folder (แทน One-File)
- แก้ไข `build_exe.spec` → เปลี่ยน `onefile=True` เป็น `onefile=False`
- ได้โฟลเดอร์ที่มีไฟล์หลายตัว แต่เปิดเร็วกว่า

## สรุป

การสร้าง .exe ทำให้:
- **ผู้ใช้ทั่วไป** ใช้งานง่ายโดยไม่ต้องมีความรู้ด้าน Python
- **แจกจ่ายง่าย** - copy ไฟล์เดียวเท่านั้น
- **ไม่ต้องติดตั้ง dependencies** - ทุกอย่างรวมอยู่แล้ว
- **พกพาได้** - ใช้งานได้บน Windows ทุกเครื่องที่ไม่มี Python
