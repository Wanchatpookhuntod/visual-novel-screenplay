# Context Menu Implementation Summary

## สิ่งที่เปลี่ยนแปลง:

### 1. ไฟล์ `views.py` (เพิ่มฟีเจอร์ใหม่)
- เพิ่ม `QMenu` import
- เพิ่ม `mousePressEvent()` และ `mouseReleaseEvent()` 
- เพิ่ม `show_context_menu()` method
- เพิ่ม `create_start_node()`, `create_scene_node()`, `create_branch_node()` methods
- เพิ่ม `update_scene_rect_for_node()` helper method
- อัปเดต `drawForeground()` เพื่อรองรับ BranchNode

### 2. ไฟล์ `graphics_items.py` (เพิ่ม BranchNode)
- เพิ่มคลาส `BranchNode` ใหม่ที่มี:
  - 1 input circle และ multiple output circles
  - สีส้มเพื่อแยกจาก node อื่น
  - Context menu สำหรับเพิ่ม/ลด output circles
  - เก็บ connection tracking แบบ multiple outputs
- อัปเดต type checking ใน existing methods เพื่อรองรับ BranchNode

### 3. ไฟล์ `main_window.py` (ปรับปรุง event handling)
- ปิดการใช้งาน direct node creation ใน `eventFilter()`
- อัปเดต status messages เพื่อให้สอดคล้องกับ context menu
- อัปเดต help text เพื่อเน้น context menu

## ฟีเจอร์ใหม่:

### Context Menu (คลิกขวาบนพื้นที่ว่าง)
- 🚀 Create Start Node - สร้าง start node (สีเขียว, ไม่มี input)
- 🎬 Create Scene Node - สร้าง scene node ปกติ (สีเทา)  
- 🌿 Create Branch Node - สร้าง branch node (สีส้ม, multiple outputs)

### BranchNode Features
- **Multiple Outputs**: มี 3 output circles เริ่มต้น
- **Add/Remove Outputs**: คลิกขวาบน branch node เพื่อเพิ่ม/ลด outputs
- **Branch Logic**: เหมาะสำหรับ decision points หรือ multiple story paths
- **Connection Tracking**: เก็บรายชื่อ nodes ที่เชื่อมต่อกับแต่ละ output

### การใช้งาน:
1. **คลิกขวาบนพื้นที่ว่าง** → เลือกประเภท node ที่ต้องการสร้าง
2. **คลิกขวาบน branch node** → เลือก "Add Output" หรือ "Remove Output"
3. **Double-click บน node ใดๆ** → เปิดฟอร์มแก้ไข
4. **Drag จาก output circle ไป input circle** → สร้างการเชื่อมต่อ

## ข้อดี:
- **User-Friendly**: เมนูที่ชัดเจนแทนการสร้าง node แบบเดิม
- **Flexible Branching**: รองรับ story branching ที่ซับซ้อน
- **Visual Distinction**: สีที่แตกต่างสำหรับแต่ละประเภท node
- **Scalable Outputs**: เพิ่ม/ลด output ได้ตามต้องการ

## สีของ Node Types:
- **Start Node**: สีเขียว (Green) - จุดเริ่มต้นเรื่อง
- **Scene Node**: สีเทา (Gray) - ฉากปกติ
- **Branch Node**: สีส้ม (Orange) - จุดแยกเส้นเรื่อง

ตอนนี้โปรแกรมพร้อมใช้งานด้วย context menu ที่ครบถ้วนและ BranchNode สำหรับ story branching!
