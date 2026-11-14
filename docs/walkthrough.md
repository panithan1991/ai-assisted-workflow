# ทดลองงานหนึ่งชิ้นตั้งแต่รับโจทย์จนจำลองยืนยันส่ง

ตัวอย่างนี้เป็นรายงานสมมติของ DEMO101 ไม่ใช้รายงานนักศึกษา ข้อมูลรายวิชาจริง หรือบัญชีบริการ ค่า "ตรวจผ่าน" และ "ยืนยันส่ง" ในตัวอย่างเป็นข้อมูลจำลองทั้งหมด

ใช้ Python 3.10 ขึ้นไป เปิดเทอร์มินัลที่รากชุด Blueprint แล้วรัน:

```sh
python -B tools/demo_workflow.py
```

โปรแกรมอ่าน [โจทย์สมมติ](../examples/walkthrough/assignment.json) แล้วทำงานใน temporary directory ของเครื่อง ไม่เปลี่ยนโจทย์ตัวอย่าง ไม่เรียก AI ไม่ฝึกโมเดล และไม่ส่งข้อมูลไปที่ใด เมื่อจบจะล้างเฉพาะไฟล์ชั่วคราวที่สร้างสำหรับ demo

## 1. รับโจทย์และบันทึกสิ่งที่ต้องทำ

โจทย์เริ่มต้นให้เขียนหัวข้อ Question, Method และ Conclusion จึงเก็บรายการหัวข้อไว้ใน current_requirements ตั้ง requirements_revision=1 และ status=in_progress ยังไม่เลือก artifacts และไม่อ้างว่าผ่านการตรวจ

สิ่งที่ต้องรู้เมื่อกลับมาทำต่อคือโจทย์ปัจจุบัน ต้นทาง ฉบับงาน และ next_actions ไม่ต้องใช้ประวัติแชตเป็นแหล่งข้อกำหนดเพียงอย่างเดียว

## 2. สร้างฉบับแรกและจำลองการตรวจ

Demo สร้าง answer-v1.txt แล้วจำลองผู้ตรวจด้วย JSON ที่ระบุ passed=true, requirements_revision, artifact_revision, requirements_sha256 และ artifact_sha256

ตัวตรวจเปิดอ่านไฟล์คำตอบจริงและ JSON หลักฐาน ก่อนยอมรับการเปลี่ยนจาก in_review เป็น ready_to_submit การตั้ง passed=true เพียงที่ metadata แต่ไม่มีหลักฐานที่ตรงกันยังไม่พอ

ในงานจริง ขั้นนี้ต้องตรวจเนื้อหา การคำนวณ หรือรูปแบบตามโจทย์ก่อนบันทึกผล Demo ไม่ได้ตรวจความถูกต้องของเนื้อหาวิชาการ

## 3. โจทย์เปลี่ยนหลังตรวจผ่าน

เพิ่มหัวข้อ Limitations เข้า current_requirements โดยจงใจยังไม่เพิ่มเลข revision ตัวตรวจต้องปฏิเสธสถานะพร้อมส่ง เพราะ hash ของข้อกำหนดเปลี่ยนแล้ว

นี่คือเหตุผลที่เก็บทั้ง revision และ hash: revision ใช้สื่อสารลำดับงาน ส่วน hash ตรวจว่าข้อกำหนดที่กำลังอ่านยังเป็นเนื้อหาที่เคยตรวจหรือไม่

## 4. กลับไปทำงานและตรวจฉบับใหม่

เปลี่ยน status กลับ in_progress เพิ่ม requirements_revision เป็น 2 และ artifact_revision เป็น 2 สร้าง answer-v2.txt ที่เพิ่ม Limitations โดยคง answer-v1.txt ไว้ จากนั้นจำลองตรวจใหม่และผูกหลักฐานกับ hash ใหม่

เมื่อทุกส่วนตรงกันจึงใช้ ready_to_submit ได้อีกครั้ง ตัวตรวจไม่เขียนสถานะหรือเพิ่ม revision ให้อัตโนมัติ Demo เป็นผู้จัดลำดับการแก้ข้อมูลเพื่อสาธิตเท่านั้น

## 5. ไฟล์เปลี่ยนหลังตรวจ

Demo ทดลองเติมข้อความลง answer-v2.txt แล้วตรวจอีกครั้ง ต้องถูกปฏิเสธเพราะ checksum ไม่ตรงกับฉบับที่เคยตรวจ จากนั้นคืนไบต์เดิมเฉพาะในไฟล์ชั่วคราวของ demo

ในงานจริง เมื่อแก้เนื้อหาที่จะส่งควรเพิ่ม artifact_revision และตรวจใหม่ ไม่ใช้การเปลี่ยนชื่อไฟล์เป็น final เพื่อยืนยันว่างานผ่านแล้ว

## 6. พร้อมส่งกับส่งแล้วเป็นคนละสถานะ

ลองเปลี่ยนจาก ready_to_submit เป็น submitted โดยไม่มี submission evidence ต้องถูกปฏิเสธ เมื่อเพิ่มการยืนยัน วันเวลา และข้อความใบตอบรับสมมติ ตัวตรวจจึงยอมรับการเปลี่ยนสถานะในข้อมูลจำลอง

การตรวจนี้ไม่ส่งไฟล์และไม่ตรวจสอบใบตอบรับกับเว็บไซต์ ในงานจริงต้องมีการยืนยันและหลักฐานจริงจากผู้ใช้ก่อนบันทึก submitted

## ผลที่ควรเห็น

```text
DEMO ONLY: fictional files and simulated review; no real submission.
1. PASS: draft has requirements and no selected artifact.
2. PASS: simulated review binds requirements and answer-v1.txt.
3. EXPECTED REJECTION: changed requirements, even without a revision bump.
4. PASS: revised answer-v2.txt reviewed; answer-v1.txt is preserved.
5. EXPECTED REJECTION: artifact edited after review.
6. EXPECTED REJECTION: ready does not mean submitted.
7. PASS: simulated confirmation satisfies the contract; nothing was sent.
DONE: temporary demo files removed; repository examples unchanged.
```

การเห็น EXPECTED REJECTION เป็นผลที่ถูกต้อง โปรแกรมควรจบด้วย exit code 0 หากกลไกทำงานตามตัวอย่าง

## จากงานตัวอย่างไปสู่พื้นที่ของผู้ใช้

เริ่มจากเพิ่ม index ที่ชี้โฟลเดอร์เดิม เลือก record ปัจจุบันให้ชัด แล้วค่อยใช้ contract นี้กับงานหนึ่งงาน เก็บ configuration เฉพาะเครื่องนอกชุดสาธารณะ

สำหรับโปรเจ็คที่ยังรออนุญาตให้ทดลอง ดู [transaction-demo](../examples/projects/transaction-demo/README.md) ซึ่งแสดงการอ้าง README, context, instructions และต้นทางผ่านสารบัญ ตัวตรวจอ่านเฉพาะข้อมูลกำกับ ไม่มีการเรียก trainer หรือเปิดบริการ
