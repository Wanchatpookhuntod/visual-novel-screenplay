# Branch Node + และ - Buttons Implementation

## สิ่งที่เพิ่มเข้ามา:

### 1. คลาส `BranchButton` (ใหม่)
- ปุ่มกลมที่คลิกได้สำหรับ Branch Node
- มี hover effects (สีเปลี่ยนเมื่อเอาเมาส์ชี้)
- แสดงข้อความ + หรือ - ตรงกลางปุ่ม
- เรียก callback function เมื่อคลิก

### 2. การปรับปรุง BranchNode
- เพิ่มปุ่ม **+** ด้านบน สำหรับเพิ่ม output
- เพิ่มปุ่ม **-** ด้านล่าง สำหรับลด output
- ปุ่มจะซ่อน/แสดงตามจำนวน output ปัจจุบัน
- ป้องกันการคลิกซ้ำด้วย flag variables

### 3. ฟีเจอร์ Button Visibility
- **ปุ่ม -**: ซ่อนเมื่อมี output เพียง 1 อัน
- **ปุ่ม +**: ซ่อนเมื่อมี output ถึงขีดจำกัด (8 อัน)
- อัปเดตอัตโนมัติเมื่อเพิ่ม/ลด output

### 4. การปรับปรุง Mouse Events
- ตรวจสอบว่าคลิกบนปุ่มหรือไม่ ก่อนจัดการ drag node
- ให้ปุ่มจัดการ event เอง เพื่อไม่ขัดแย้งกับการ drag

### 5. Context Menu ที่เรียบง่าย
- ลบ "Add Output" และ "Remove Output" ออกจาก context menu
- เหลือแค่ Edit, Duplicate, Delete
- เพราะตอนนี้ใช้ปุ่ม + และ - แทน

## การใช้งาน:

### เพิ่ม Output
1. **คลิกปุ่ม +** ที่ด้านบนของ Branch Node
2. Output circle ใหม่จะปรากฏขึ้น
3. จำกัดสูงสุด 8 outputs

### ลด Output  
1. **คลิกปุ่ม -** ที่ด้านล่างของ Branch Node
2. Output circle สุดท้ายจะหายไป
3. จำกัดต่ำสุด 1 output

### Visual Feedback
- **Hover Effect**: ปุ่มเปลี่ยนสีเมื่อเอาเมาส์ชี้
- **Status Messages**: แสดงจำนวน output ปัจจุบันใน status bar
- **Button Hiding**: ปุ่มหายไปเมื่อถึงขีดจำกัด

## ข้อดี:

### User Experience
- 🎯 **ง่ายต่อการใช้**: คลิกปุ่มเดียวแทนการไปที่ context menu
- 👁️ **Visual Clarity**: เห็นปุ่มชัดเจนบน node เลย
- 🚫 **ป้องกันข้อผิดพลาด**: ปุ่มหายไปเมื่อไม่สามารถใช้ได้

### Technical
- 🔄 **Prevent Double-Click**: มี flag ป้องกันการคลิกซ้ำ
- 🎨 **Clean Integration**: ไม่รบกวนการทำงานของ node อื่น
- 📊 **Smart Visibility**: แสดง/ซ่อนปุ่มตามสถานการณ์

### Performance
- ⚡ **Direct Action**: ไม่ต้องเปิด menu แล้วเลือก
- 🎯 **Visual Feedback**: ตอบสนองทันทีเมื่อคลิก
- 💾 **Memory Efficient**: ใช้ callback แทน event listener

## สีและการออกแบบ:

### ปุ่ม + และ -
- **พื้นหลัง**: เทาเข้ม (#464646)
- **ขอบ**: เทาอ่อน (#C8C8C8) 
- **ข้อความ**: สีขาว (#FFFFFF)
- **Hover**: เทาอ่อนขึ้น (#646464) + ขอบขาว

### ตำแหน่ง
- **ปุ่ม +**: ด้านบนของ node (นอก node rect)
- **ปุ่ม -**: ด้านล่างของ node (นอก node rect)
- **ขนาด**: รัศมี 8 pixels

## สรุป:

ตอนนี้ Branch Node มีปุ่ม + และ - ที่ใช้งานง่าย ทำให้การสร้าง story branching สะดวกและเป็นมืออาชีพมากขึ้น! 🎉
