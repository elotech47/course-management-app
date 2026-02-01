Below is a clean blueprint for building your **lab course management + digital rubric grading system** (React frontend + FastAPI backend), based on the roles/rubrics you shared .

---

## 1) What the system must do (core workflow)

1. **Instructor/TA logs in**
2. **Create a Course** (e.g., “ME 4611 – Section 1”)
3. **Add students** (name + email)
4. **Create semester schedule** (weeks/classes)
5. **Assign roles each week** (TT, TM, Camera, SMT, Lead, Reporter)
6. **Grade each student per week**

   * App automatically loads the correct **rubric template** for that role (Toastmaster, Table Topic, Camera Assistant, Group Leader, Group Reporter, 6-min talk) 
   * TA enters scores + deductions + comments
7. **Save grade + rubric snapshot**
8. **Email student the graded rubric** (PDF or HTML)
9. **End of term:** generate grade sheet export (Excel/CSV) like your example

---

## 2) Key product screens (Frontend)

### A. Auth + Org

* Sign up / login
* “My Courses” dashboard

### B. Course Setup

* Course settings (semester start/end, meeting days, grading policy)
* Student roster upload (CSV import: name,email)

### C. Schedule Builder

* Calendar-like view: rows = students, columns = weeks/classes
* Assign roles by dropdown (bulk fill, auto-rotate, conflict detection)
* Optional: copy schedule from previous semester

### D. Grading Workspace (the main productivity screen)

* Pick: **Course → Week/Class → Group**
* Left: list of students with assigned role + grading status
* Right: rubric form auto-loads for the student’s role:

  * Sliders/step inputs matching rubric points (0–10, 0–20, etc.)
  * Deductions section
  * Comments box
* One-click: “Save + Next Student”
* One-click: “Send rubric email”

### E. Reports

* Student profile: all weeks, role history, scores, comments
* Grade summary table (by role type + totals)
* Export:

  * CSV/Excel grade sheet
  * PDF grade summaries (optional)

---

## 3) Data model (Backend + DB)

Use **PostgreSQL**.

### Core entities

* **User** (instructor/TA)
* **Course**
* **Enrollment** (user ↔ course role: Instructor/TA)
* **Student** (belongs to course)
* **ClassSession** (one per week/date: e.g., 2025-10-20)
* **RoleAssignment** (student + class_session + role)
* **RubricTemplate** (Toastmaster, Table Topic, etc.)
* **RubricCriterion** (each row/line item in rubric)
* **GradeRecord** (one per student per class_session)
* **GradeCriterionScore** (criterion scores)
* **GradeDeduction** (deductions applied)
* **RubricSnapshot** (frozen copy used for emailing + auditing)
* **EmailLog** (sent status, timestamps, retry info)

### Why “RubricSnapshot” matters

Rubrics change over time. You want the **exact rubric version** used that week preserved (and attached to the email). This matches your “we email the student their graded rubric each week” requirement.

---

## 4) How to represent your rubrics digitally

Convert each rubric into a template with:

* criteria list
* scoring scale per criterion
* max points
* deduction rules
* total calculation rules

Examples from your rubric PDF:

* **Toastmaster**: moderation criteria (0–10), comments feedback, deductions, total /40 
* **Table Topic**: presentation criteria (0–10), comments feedback, speaking time deduction, total /40 
* **Camera Assistant**: 3 criteria (0–20 step 2), deductions, total /40 
* **Group Leader/Reporter/6-min talk**: multi-section scoring, deductions, total /200 

**Implementation detail:** store rubric criteria as structured JSON or normalized tables. I recommend normalized tables for analytics + reporting, but JSON works fine for v1.

---

## 5) Backend architecture (FastAPI)

### Stack

* **FastAPI**
* **Postgres**
* **SQLAlchemy 2.0** + Alembic migrations
* Auth: **JWT** (or session cookies if you prefer)
* Email: SendGrid/Mailgun/SES
* Background jobs: **Celery + Redis** (or RQ) for email + PDF generation
* File storage: S3 (or local dev)

### API modules

* `auth/`
* `courses/`
* `students/`
* `sessions/`
* `roles/assignments/`
* `rubrics/`
* `grading/`
* `reports/`
* `exports/`

### Minimal endpoints (practical MVP)

**Course + roster**

* `POST /courses`
* `GET /courses`
* `POST /courses/{course_id}/students:bulk_import`
* `GET /courses/{course_id}/students`

**Schedule**

* `POST /courses/{course_id}/sessions`
* `GET /courses/{course_id}/sessions`
* `POST /sessions/{session_id}/assignments` (bulk assignments)

**Rubrics**

* `GET /rubric-templates`
* `GET /rubric-templates/{role}`

**Grading**

* `POST /grade-records` (creates grade + snapshot)
* `PUT /grade-records/{id}`
* `GET /sessions/{session_id}/grade-records`

**Email**

* `POST /grade-records/{id}/send-email`
* `GET /email-logs?course_id=...`

**Export**

* `GET /courses/{course_id}/export/final-grades.csv`
* `GET /courses/{course_id}/export/final-grades.xlsx`

---

## 6) Grading logic

For each GradeRecord:

1. Determine assigned role (TT/TM/Camera/SMT/Lead/Reporter)
2. Load matching RubricTemplate
3. Validate scores follow allowed scale (e.g., 0–10, step 1; 0–20, step 2)
4. Apply deductions
5. Compute:

   * section subtotals
   * total
   * course running totals

Store:

* raw criterion scores
* deductions
* computed totals
* snapshot of rubric + scoring

---

## 7) Emailing the graded rubric (weekly)

Two solid options:

### Option A: PDF attachment (recommended)

* Render HTML template → convert to PDF (WeasyPrint / wkhtmltopdf)
* Attach PDF and email student

### Option B: HTML email

* Faster; but harder to keep formatting consistent

You can also include:

* role + date + score breakdown
* TA/instructor comments
* link to “student portal” view (optional)

---

## 8) Permissions & security (must-have)

* Course-scoped access:

  * Instructor: manage everything
  * TA: grade + view course data (maybe restricted to section)
* Student access (optional for v2):

  * view rubrics/grades history

---

## 9) MVP build plan (fast, realistic)

### Phase 1 (MVP you can use this semester)

* Auth
* Course + students
* Sessions (weeks/dates)
* Role assignment grid
* Rubric templates seeded from your rubrics 
* Grading UI + saving grade records
* Export CSV

### Phase 2

* Email graded rubric + PDF snapshots
* Full “final grade sheet” Excel output like your screenshot
* Analytics + per-role totals

### Phase 3

* Auto-rotation role assignment + constraint solver
* Student portal
* Multi-section support / multiple instructors

---

## 10) Suggested frontend tech

* **React + TypeScript**
* UI: MUI or shadcn/ui
* Forms: react-hook-form
* Tables: TanStack Table (schedule grid)
* State: Zustand (or React Query + minimal state)
* PDF preview: server-generated PDF

