# Data contracts

Data contract คือข้อตกลงว่าแต่ละไฟล์ต้องมีข้อมูลอะไร ใครเป็นผู้แก้ และส่วนอื่นอ่านข้อมูลใดเป็นหลัก

## หลักเรื่องแหล่งข้อมูล

หนึ่งข้อเท็จจริงมีเจ้าของเพียงที่เดียว:
- workspace index เก็บเส้นทาง ไม่เก็บโจทย์หรือสถานะส่งงานซ้ำ
- course context เก็บบทปัจจุบันและเส้นทางงาน
- assignment context เก็บข้อกำหนดปัจจุบัน สถานะ และรายการฉบับที่เลือก
- verification ผูกกับรุ่นของข้อกำหนดและรุ่นของผลงาน
- history เก็บเหตุการณ์ก่อนหน้า โดยไม่ถูกอ่านเป็นค่า default

## Assignment fields

| Field | ความหมาย |
|---|---|
| schema_version | รุ่นของรูปแบบข้อมูล |
| id, course_id | รหัสคงที่ ไม่เปลี่ยนตามชื่อไฟล์ |
| status | inbox / in_progress / in_review / ready_to_submit / submitted / archived |
| requirements_revision | รุ่นข้อกำหนดปัจจุบัน เพิ่มเมื่ออาจารย์/ผู้เรียนเปลี่ยน scope |
| artifact_revision | รุ่นผลงานปัจจุบัน เพิ่มเมื่อเนื้อหาที่จะส่งเปลี่ยน |
| current_requirements | เฉพาะข้อกำหนดปัจจุบัน ไม่รวมข้อความที่ถูกแทนแล้ว |
| sources | หลักฐานต้นทางของโจทย์หรือคำแก้ไข |
| artifacts | รายการฉบับที่เลือกพร้อม path, SHA-256 และ revision |
| verification | ผ่าน/ไม่ผ่าน ตรวจรุ่นใดบ้าง และลิงก์หลักฐานตรวจ |
| submission | หลักฐานการส่งจริง หรือ null |
| next_actions | สิ่งที่ยังต้องทำ |

## เงื่อนไขความพร้อม

ready_to_submit ต้องมี:
- รายการ artifacts ที่ไม่ว่าง ทุกไฟล์เป็นรุ่นผลงานปัจจุบัน
- checksum SHA-256 และที่อยู่ไฟล์
- verification.passed = true
- verification.requirements_revision ตรงกับปัจจุบัน
- verification.artifact_revision ตรงกับปัจจุบัน
- verification.requirements_sha256 ตรงกับเนื้อหา current_requirements ปัจจุบัน แม้มีการลืมเพิ่ม revision
- verification.evidence ชี้ไฟล์ JSON ที่เปิดอ่านได้และระบุผ่านสำหรับข้อกำหนด รุ่น และไฟล์ที่เลือก

submitted และ archived ต้องผ่านเงื่อนไขเดียวกันและมี submission ซึ่งระบุการยืนยันโดยผู้ใช้ วันเวลา และหลักฐาน

การเพิ่ม artifact revision ทำให้ผลตรวจเก่าใช้ไม่ได้เช่นเดียวกับการแก้ข้อกำหนด

### เอกลักษณ์ของข้อกำหนด

ตัวตรวจคำนวณ SHA-256 ด้วยรูปแบบเดียวกับระบบจริง:

```python
payload = json.dumps(current_requirements, ensure_ascii=False,
                     sort_keys=True, separators=(",", ":"), allow_nan=False)
requirements_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

ใช้ค่า JSON ที่ถูกต้องและไม่ใส่ NaN หรือ Infinity การสลับลำดับ key ไม่ทำให้ hash เปลี่ยน แต่การแก้ค่า เช่น จำนวนหน้า ทศนิยม หรือรายการหัวข้อ ทำให้ผลตรวจเดิมใช้ต่อไม่ได้ ต้องเพิ่ม revision และตรวจงานใหม่ตามปกติด้วย

### ไฟล์หลักฐานตรวจ

หลักฐานแต่ละไฟล์เป็น JSON object ที่มี fields ดังนี้:

| Field | สิ่งที่ต้องตรง |
|---|---|
| passed | เป็น true หลังมีการตรวจตามเกณฑ์ของงาน |
| requirements_revision | รุ่นข้อกำหนดปัจจุบัน |
| artifact_revision | รุ่นผลงานปัจจุบัน |
| requirements_sha256 | hash ของ current_requirements ที่ตรวจ |
| artifact_sha256 | hash ของไฟล์หนึ่งไฟล์ในรายการ artifacts |

เมื่อเลือกหลายไฟล์ ต้องมีหลักฐานที่ตรงกับทุกไฟล์ โดยลงรายการหลักฐานทั้งหมดใน verification.evidence ไม่ใช้เพียงไฟล์ข้อความที่เขียนว่า "ผ่าน" หรือรายงานของงานอีกชิ้นมารับรองแทน

ตัวตรวจอ่านข้อมูลที่บันทึกไว้ ไม่พิสูจน์ว่าใครเป็นผู้ตรวจหรือการตรวจเนื้อหาครบถ้วนหรือไม่ ใน demo ค่า passed=true เป็นการจำลองเพื่อแสดง contract เท่านั้น ไม่ใช่การรับรองงานวิชาการ

## Project registry

รายการ projects ใน workspace index เก็บ id, course_id, path และ entry พร้อม current_context, instructions และ references เมื่อมี โดย path ทั้งหมดอ้างจากราก workspace ของตัวอย่าง

course context ใช้ project_ids อ้างรายการนี้ ตัวตรวจตรวจทั้งรหัสวิชา รหัสโปรเจ็ค และไฟล์ปลายทาง เช่น project_id ใน project-context.json ต้องตรงกับ id ในสารบัญ การตรวจรายการโปรเจ็คไม่ import โค้ดโปรเจ็คหรือเปิด runtime

ในระบบที่มี metadata เก่า ให้ index ชี้ record ปัจจุบันโดยตรง เช่น _workspace/state/assignments/... ไม่เดาว่า assignment-context.json ทุกไฟล์เป็นแหล่งหลัก ชื่อและตำแหน่ง record เปลี่ยนได้ตามพื้นที่ แต่ต้องมีเจ้าของข้อกำหนดปัจจุบันชุดเดียว

## Feedback record

Feedback เป็น record แยกจาก assignment จึงไม่ทำให้งานเดิมหรือผู้ใช้ที่ข้ามการตอบถูกตัดสินว่าไม่พร้อมส่ง ดู [ตัวอย่างสมมติ](../examples/feedback/pending.json) และ [วงจรการใช้งาน](feedback-loop.md)

- delivery เก็บ delivery_id, task_id, requirements_revision, requirements_sha256, artifact_revision และรายการ path/hash ของชิ้นงาน ถ้าเป็นคำตอบในแชตให้มี content_sha256 แทนไฟล์
- delivery_sha256 คำนวณจาก canonical JSON ของ delivery เพื่อผูกความเห็นกับฉบับที่ผู้ใช้เห็น สร้าง snapshot จากไฟล์/เนื้อหาที่ส่งจริง และเปรียบเทียบกับฉบับปัจจุบันก่อนนำ feedback มาใช้
- objective_verification.status ใช้ passed / failed / not_checked / not_applicable และอ้างหลักฐานตามงาน ไม่สร้างคะแนนรวมจากความพึงพอใจ
- feedback.status ใช้ pending / responded / skipped โดย pending และ skipped มี response=null ไม่เดาคำตอบจากความเงียบ
- response เมื่อผู้ใช้ตอบ ต้องมี choice เป็น accepted / adjust / off_target, source=user, received_at และ delivery_sha256 ที่ตรงกับคำถามเดิม

ตัวตรวจ Feedback ตรวจรูปแบบและความสอดคล้องของ snapshot ไม่รับรองว่าผู้ใช้ตอบจริงหรือไฟล์ปัจจุบันยังเหมือน snapshot ผู้บันทึกต้องมีคำตอบผู้ใช้และตรวจไฟล์จริงก่อนผูก record การตรวจ checksum/หลักฐานงานจริงยังเป็นหน้าที่ของ assignment verification

Feedback ของฉบับเก่ายังคงถูกต้องในฐานะประวัติ แต่ feedback_applies_to_delivery จะคืน false เมื่อเทียบกับ snapshot ฉบับใหม่ คำว่า accepted ไม่ได้เปลี่ยนผลตรวจ failed ให้ passed ไม่เปลี่ยนเป็น submitted และไม่อนุญาตรันโมเดลหรือเผยแพร่

พื้นที่ใช้งานจริงเก็บนโยบายและ record ใน _workspace/state/feedback/ ซึ่งเป็นข้อมูลส่วนตัว ชุด Blueprint เก็บเฉพาะตัวอย่างจำลอง ไม่คัดคำตอบผู้ใช้จริงเข้าตัวอย่าง

## รูปแบบที่แบ่งปันกับ configuration จริง

ตัวอย่างใน repository ใช้ path สัมพัทธ์และข้อมูลจำลอง Configuration จริงของเครื่องใช้ local overlay ซึ่งไม่เข้า Git เช่น ที่อยู่ interpreter, ตำแหน่งบริการภายนอก และ credentials

env.is_cuda_available เป็นผลตรวจจาก environment นั้น ไม่ใช่การคัดค่า CUDA version ของ driver มาแทน หากยังไม่ได้ตรวจให้เก็บค่า null และ verified=false

## ขอบเขตของโปรแกรมตรวจ

tools/check_blueprint.py เป็น reference checker ขนาดเล็ก:
- ตรวจ fields และ invariants หลักของ assignment
- ตรวจว่ารายการวิชาชี้ไปยังตัวอย่างที่มีจริง
- ตรวจ transition guards
- ไม่เปิด source URL หรือเรียก AI
- เมื่อทดสอบสถานะพร้อมส่ง ตรวจไฟล์จริง checksum และเนื้อหา JSON หลักฐานภายใน root ของงาน ให้ผูกกับข้อกำหนดและฉบับงานปัจจุบันครบทุกไฟล์
- ตัวอย่างเริ่มใน in_progress และไม่มี artifacts จึงไม่กล่าวอ้างว่ามี PDF พร้อมส่ง
- เมื่อใช้กับ workspace จริง ยังต้องตรวจเนื้อหา การคำนวณ และรูปแบบตาม acceptance criteria ของงานนั้น

SHA-256 เป็นหลักฐานว่าไฟล์ยังเป็นไฟล์รุ่นเดิม ไม่ใช่หลักฐานว่าเนื้อหาในไฟล์ถูกต้อง
