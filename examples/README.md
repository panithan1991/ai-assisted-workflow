# Examples

ไฟล์ทั้งหมดในโฟลเดอร์นี้เป็นข้อมูลจำลองสำหรับสาธิตโครงสร้าง ไม่ใช่สถานะส่งงานจริงของผู้เรียน

- workspace.json: สารบัญของสามวิชา
- environments.json: ตัวเลือก runtime ที่ยังไม่ยืนยันความพร้อม
- courses/*/course-context.json: บทตัวอย่างและที่อยู่ assignment
- courses/DADS6003/Assignments/NN_homework/assignment-context.json: ตัวอย่างงานที่แก้โจทย์เหลืออนุพันธ์ 3 ตัว
- courses/DADS6003/Assignments/NN_homework/history.json: เหตุการณ์แก้ข้อกำหนด
- projects/transaction-demo/: โปรเจ็คสมมติที่สารบัญชี้ไปยัง README สถานะหลัก กติกา และต้นทาง โดยไม่รันโมเดล
- walkthrough/assignment.json: โจทย์รายงานสมมติของ DEMO101 สำหรับ [ตัวอย่างทีละขั้น](../docs/walkthrough.md)
- feedback/pending.json: Feedback สมมติที่ยังไม่มีคำตอบ แยกจากผลตรวจและผูกกับฉบับที่ส่งมอบ

ตัวอย่างตั้งสถานะ in_progress, artifacts ว่าง และ verification.passed=false เพื่อไม่กล่าวอ้างว่ามีงานพร้อมส่งหรือ environment ที่ตรวจผ่านแล้ว

ตัวอย่างโปรเจ็คตั้งสถานะรอเลือกแนวทาง ส่วน demo สร้างไฟล์คำตอบและ JSON หลักฐานจำลองใน temporary directory แล้วล้างเฉพาะไฟล์จำลองเหล่านั้นเมื่อจบ ไม่อ่านหรือเปลี่ยนสถานะงานจริง
