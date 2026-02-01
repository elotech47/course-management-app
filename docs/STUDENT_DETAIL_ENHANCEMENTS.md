# Student Detail Enhancements

## Summary
Enhanced the student detail page with new reporting and PDF generation features. Removed email functionality and added comprehensive grade report viewing and export capabilities.

## Changes Made

### 1. Frontend - StudentDetail.tsx
**Location**: `/frontend/src/pages/StudentDetail.tsx`

**Changes**:
- Replaced "Send Email" button with "View Report" button
- Added navigation to student-specific report page
- Added "Download PDF" button for each session in the Grade History table
- Added `session_id` to the `GradeDetail` interface
- Integrated toast notifications for PDF downloads
- Added PDF download handler with loading states

**Key Features**:
- Click "View Report" navigates to `/students/:studentId/report`
- Click "PDF" button in any grade history row downloads that session's graded rubric as PDF
- Toast notifications provide feedback on PDF generation progress

### 2. Frontend - StudentReport.tsx (NEW)
**Location**: `/frontend/src/pages/StudentReport.tsx`

**Purpose**: Dedicated page showing student's grade report in Excel-like format

**Features**:
- Displays sessions as rows, roles as columns
- Shows "Total Score" (max possible points) and "Obtained Score" (actual points)
- "Export Excel" button to download the report
- Same visual format as the course-wide report but focused on one student
- Proper role-based score calculation matching the course report

**Layout**:
```
STUDENT NAME: CHLOE BLANCHARD

DATES       | TT  | TM  | CAMERA | SMT | LEAD | REPORTER | TOTAL SCORE
01/12/26    | 33  | -   | -      | -   | -    | -        | 33
01/19/26    | -   | 34  | -      | -   | -    | -        | 34
Total Score | 40  | 40  | 0      | 0   | 0    | 0        | 80
Obtained Score | 33 | 34 | 0    | 0   | 0    | 0        | 67
```

### 3. Frontend - App.tsx
**Location**: `/frontend/src/App.tsx`

**Changes**:
- Imported `StudentReport` component
- Added route: `/students/:studentId/report`

### 4. Backend - reports.py
**Location**: `/backend/app/api/routes/reports.py`

**Changes**:
1. **Updated `/student/{student_id}/summary` endpoint**:
   - Added `session_id` to the `grade_details` response
   - This allows the frontend to know which session each grade belongs to for PDF download

2. **Added new `/student/{student_id}/grade-sheet` endpoint**:
   - Returns grade data for a single student in Excel-like format
   - Includes `session_headers`, `role_totals`, `role_counts`
   - Matches the structure of the course-wide grade sheet but for one student

**Response Structure**:
```json
{
  "student_id": 1,
  "student_name": "Chloe Blanchard",
  "student_number": "",
  "sessions": [
    {
      "session_id": 1,
      "role": "TT",
      "score": 33
    },
    ...
  ],
  "role_totals": {
    "TT": 33,
    "TM": 34,
    "Camera": 0,
    ...
  },
  "role_counts": {
    "TT": 1,
    "TM": 1,
    "Camera": 0,
    ...
  },
  "total_score": 67,
  "session_headers": [
    {
      "id": 1,
      "date": "01/12/26",
      "session_number": 1,
      "title": "Practise"
    },
    ...
  ]
}
```

### 5. Backend - exports.py
**Location**: `/backend/app/api/routes/exports.py`

**Changes**:
1. **Replaced `/student/{student_id}/report` endpoint with `/student/{student_id}/grades.xlsx`**:
   - Now generates Excel file matching the Excel-like report format
   - Shows sessions as rows, roles as columns
   - Includes "Total Score" and "Obtained Score" rows
   - Properly calculates max possible vs obtained scores per role

2. **Added new `/student/{student_id}/session/{session_id}/rubric.pdf` endpoint**:
   - Generates a PDF of the graded rubric for a specific student and session
   - Shows all criteria with obtained scores filled in
   - Includes deductions section
   - Shows raw score, deductions, and final score
   - Displays feedback names for YouTube comments

### 6. Backend - pdf_generator.py (NEW)
**Location**: `/backend/app/services/pdf_generator.py`

**Purpose**: Generate professional PDF rubrics with scores filled in

**Features**:
- Uses ReportLab for PDF generation
- Hierarchical rubric structure support (sections and subsections)
- Color-coded sections (blue headers, red deductions)
- Displays:
  - Student name and session info
  - All rubric criteria with max and obtained points
  - Deductions table (if any)
  - Summary with raw score, deductions, and final score
  - Feedback names for YouTube comments (e.g., "YouTube Comment (John Doe)")

**PDF Structure**:
```
Grading Rubric - TT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Student: Chloe Blanchard        Session: Practise
Date: 01/12/2026                Role: TT

Opening (20 points)
  Attention Getter
    Description: Captures audience attention...
    ┌─────────────────────┬─────────────┬──────────────────┐
    │ Criteria            │ Max Points  │ Obtained Points  │
    ├─────────────────────┼─────────────┼──────────────────┤
    │ Effectiveness       │ 10          │ 8                │
    │ Creativity          │ 10          │ 9                │
    └─────────────────────┴─────────────┴──────────────────┘

Body Content (20 points)
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Raw Score: 35 points
Deductions: -2 points
Final Score: 33 / 40 points
```

## API Endpoints Summary

### New Endpoints
1. `GET /api/reports/student/{student_id}/grade-sheet`
   - Returns student grade data in Excel-like format

2. `GET /api/exports/student/{student_id}/grades.xlsx`
   - Downloads student grades as Excel file

3. `GET /api/exports/student/{student_id}/session/{session_id}/rubric.pdf`
   - Downloads graded rubric as PDF for a specific session

### Modified Endpoints
1. `GET /api/reports/student/{student_id}/summary`
   - Now includes `session_id` in grade_details

## User Workflow

### View Report
1. Navigate to student detail page
2. Click "View Report" button
3. See Excel-like grade sheet for that student
4. Click "Export Excel" to download

### Download PDF Rubric
1. Navigate to student detail page
2. In the "Grade History" table, find the session
3. Click the "PDF" button for that session
4. PDF downloads with all rubric details and scores filled in

## File Modifications Summary
- **Modified**: 4 files
  - `frontend/src/pages/StudentDetail.tsx`
  - `frontend/src/App.tsx`
  - `backend/app/api/routes/reports.py`
  - `backend/app/api/routes/exports.py`

- **Created**: 2 files
  - `frontend/src/pages/StudentReport.tsx`
  - `backend/app/services/pdf_generator.py`

## Testing Checklist
- [ ] Click "View Report" from student detail page
- [ ] Verify report shows correct sessions and scores
- [ ] Export Excel from student report page
- [ ] Verify Excel file matches UI display
- [ ] Download PDF from grade history table
- [ ] Verify PDF shows all rubric criteria with scores
- [ ] Check PDF displays deductions correctly
- [ ] Verify PDF shows feedback names for YouTube comments

## Notes
- The backend uses `--reload`, so changes are automatically applied
- PDF generation uses ReportLab, which is already in requirements.txt
- All toast notifications use react-hot-toast for consistency
- The student Excel export matches the same format as course exports
