# Updated Export Format to Match Excel Sheet

## Overview
Completely rewrote the CSV and Excel export functions to match the exact format shown in the provided Excel sheet, where each student gets their own section with sessions as rows.

## Changes Made

### File: `backend/app/api/routes/exports.py`

## New Format Structure

### For Each Student:
```
STUDENT NAME: ADAM DALFERES

DATES       | TT  | TM  | CAMERA | SMT | LEAD | REPORTER | TOTAL SCORE
01/12/26    | -   | 37  | -      | -   | -    | -        | 37
01/19/26    | -   | -   | -      | 211 | -    | -        | 211
Total Score | 0   | 37  | 0      | 211 | 0    | 0        | 248
Obtained Score | 0 | 37 | 0     | 211 | 0    | 0        | 248

[blank rows]

STUDENT NAME: ANTHONY MOCANU
...
```

## CSV Export (`/api/exports/course/{course_id}/grades.csv`)

### Structure:
1. **Student Header**: `STUDENT NAME: [NAME IN UPPERCASE]`
2. **Blank Row**
3. **Column Headers**: DATES, TT, TM, CAMERA, SMT, LEAD, REPORTER, TOTAL SCORE
4. **Session Rows**: One row per session with:
   - Date in `mm/dd/yy` format
   - Score in the appropriate role column
   - `-` for empty columns
   - Total score for that session
5. **Total Score Row**: Sum of all scores by role (in red in web display)
6. **Obtained Score Row**: Same as total score
7. **Blank Rows**: 2 blank rows between students

### Key Features:
- ✅ Each student gets their own section
- ✅ Sessions shown as rows (not columns)
- ✅ Scores appear in the correct role column
- ✅ Role totals calculated automatically
- ✅ Clean separation between students

## Excel Export (`/api/exports/course/{course_id}/grades.xlsx`)

### Structure:
Same data structure as CSV but with enhanced formatting:

### Styling:
1. **Student Names**: 
   - Bold, 12pt font
   - Uppercase
   - Format: "STUDENT NAME: [NAME]"

2. **Column Headers**:
   - Bold, 11pt font
   - Gray background (`#D3D3D3`)
   - Centered alignment
   - Bordered

3. **Data Cells**:
   - Centered alignment
   - Bordered
   - Numbers or "-" for empty

4. **Total Score Row**:
   - Red font, bold
   - Light red background (`#FFE4E1`)
   - Bordered
   - Label: "Total Score"

5. **Obtained Score Row**:
   - Regular font
   - Bordered
   - Label: "Obtained Score"

6. **Column Widths**: Auto-sized to 15 characters

### Implementation Details:
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Styles
header_font = Font(bold=True, size=11)
header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
total_fill = PatternFill(start_color="FFE4E1", end_color="FFE4E1", fill_type="solid")
total_font = Font(bold=True, color="FF0000")
center_align = Alignment(horizontal="center", vertical="center")
border = Border(...)
```

## Data Logic

### Role Score Placement:
```python
# For each session, score goes in the correct column
col_map = {
    "TT": 2,      # Column B
    "TM": 3,      # Column C
    "Camera": 4,  # Column D
    "SMT": 5,     # Column E
    "Lead": 6,    # Column F
    "Reporter": 7 # Column G
}
```

### Calculation:
```python
# Track totals by role
role_totals = {
    "TT": 0,
    "TM": 0,
    "Camera": 0,
    "SMT": 0,
    "Lead": 0,
    "Reporter": 0
}

# For each grade, add to appropriate role
if grade and assignment:
    score = round(grade.final_score)
    role = assignment.role.value
    role_totals[role] += score
    
# Total score = sum of all role scores
total_score = sum(role_totals.values())
```

## Comparison: Old vs New

### Old Format (Row per Student):
```
Student Name | Student ID | Session 1 | Session 2 | TT Total | TM Total | ...
Adam         | 123        | TM: 37    | SMT: 211  | 0        | 37       | ...
Anthony      | 456        | TT: 37    | -         | 37       | 0        | ...
```
❌ All students in one table  
❌ Sessions as columns  
❌ Hard to read and compare

### New Format (Section per Student):
```
STUDENT NAME: ADAM DALFERES
DATES    | TT | TM | CAMERA | SMT | LEAD | REPORTER | TOTAL
01/12/26 | -  | 37 | -      | -   | -    | -        | 37
01/19/26 | -  | -  | -      | 211 | -    | -        | 211
Total    | 0  | 37 | 0      | 211 | 0    | 0        | 248

STUDENT NAME: ANTHONY MOCANU
...
```
✅ Each student gets their own section  
✅ Sessions as rows (chronological)  
✅ Easy to read and print  
✅ Matches provided Excel format exactly

## Benefits

1. **Readability**: Each student's grades are grouped together
2. **Printability**: Easy to print individual student sections
3. **Consistency**: Matches the school's existing Excel format
4. **Clarity**: Clear role totals at a glance
5. **Flexibility**: Easy to copy sections for individual reports

## Usage

### From Frontend:
```typescript
// Export CSV
const response = await api.get(`/api/exports/course/${courseId}/grades.csv`, {
  responseType: 'blob'
})

// Export Excel
const response = await api.get(`/api/exports/course/${courseId}/grades.xlsx`, {
  responseType: 'blob'
})
```

### Download Handling:
```typescript
const url = window.URL.createObjectURL(new Blob([response.data]))
const link = document.createElement('a')
link.href = url
link.setAttribute('download', filename)
document.body.appendChild(link)
link.click()
link.remove()
```

## Testing Checklist

- [ ] CSV export generates correct format
- [ ] Excel export generates correct format with styling
- [ ] Each student has their own section
- [ ] Sessions appear in chronological order
- [ ] Scores appear in correct role columns
- [ ] Empty columns show "-"
- [ ] Total Score row sums correctly
- [ ] Obtained Score row matches Total Score
- [ ] Spacing between students is correct
- [ ] Excel styling matches specifications
- [ ] File downloads with correct filename
- [ ] Format matches provided Excel sheet

## Related Files
- `backend/app/api/routes/exports.py` - Export endpoint implementations
- `frontend/src/pages/Reports.tsx` - Export button handlers (if needed)
