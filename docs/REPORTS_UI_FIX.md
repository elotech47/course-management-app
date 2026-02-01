# Reports UI Total Score Fix

## Issue
The Reports page UI was showing obtained scores in the "Total Score" row instead of maximum possible scores. The CSV and Excel exports were correct, but the web UI needed updating.

## Root Cause
The backend `/api/reports/course/{course_id}/grade-sheet` endpoint was only calculating `role_totals` (sum of obtained scores) and not tracking `role_counts` (number of times each role was performed).

## Solution

### Backend Changes (`backend/app/api/routes/reports.py`)

Added `role_counts` tracking to the grade-sheet endpoint:

```python
row = {
    "student_id": student.id,
    "student_name": student.full_name,
    "student_number": student.student_id or "",
    "sessions": [],
    "role_totals": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
    "role_counts": {"TT": 0, "TM": 0, "Camera": 0, "SMT": 0, "Lead": 0, "Reporter": 0},
    "total_score": 0
}

# Track both obtained scores and role counts
if grade and assignment:
    role = assignment.role.value
    row["role_totals"][role] += grade.final_score  # Obtained score
    row["role_counts"][role] += 1                   # Count for max calculation
    row["total_score"] += grade.final_score
```

### Frontend Changes (`frontend/src/pages/Reports.tsx`)

1. **Updated `StudentRow` interface** to include `role_counts`:

```typescript
interface StudentRow {
  student_id: number
  student_name: string
  student_number: string
  sessions: SessionGrade[]
  role_totals: Record<string, number>      // Obtained scores
  role_counts: Record<string, number>      // Number of times role performed
  total_score: number
}
```

2. **Calculate both possible and obtained scores**:

```typescript
// Define max points per role
const roleMaxPoints: Record<string, number> = {
  'TT': 40,
  'TM': 40,
  'Camera': 40,
  'SMT': 480,
  'Lead': 400,
  'Reporter': 400
}

// Calculate totals
let totalPossibleScore = 0
let totalObtainedScore = 0

for (const role of ['TT', 'TM', 'Camera', 'SMT', 'Lead', 'Reporter']) {
  const count = student.role_counts[role] || 0
  const maxPoints = roleMaxPoints[role] || 0
  totalPossibleScore += count * maxPoints      // Max possible
  totalObtainedScore += student.role_totals[role] || 0  // Obtained
}
```

3. **Updated Total Score row** to show maximum possible points:

```typescript
<tr className="bg-red-50 font-semibold border-t-2 border-red-300">
  <td className="px-4 py-3 text-sm text-red-700">Total Score</td>
  <td className="px-4 py-3 text-center text-sm text-red-700">
    {(student.role_counts.TT || 0) * 40}
  </td>
  <!-- etc for other roles -->
  <td className="px-4 py-3 text-center text-sm font-bold text-red-700">
    {totalPossibleScore}
  </td>
</tr>
```

4. **Kept Obtained Score row** showing actual earned points:

```typescript
<tr className="bg-gray-50">
  <td className="px-4 py-3 text-sm text-gray-700">Obtained Score</td>
  <td className="px-4 py-3 text-center text-sm text-gray-700">
    {Math.round(student.role_totals.TT || 0)}
  </td>
  <!-- etc for other roles -->
  <td className="px-4 py-3 text-center text-sm font-bold text-gray-700">
    {Math.round(totalObtainedScore)}
  </td>
</tr>
```

## Result

### Before
- **Total Score**: Showed sum of obtained scores (e.g., 248)
- **Obtained Score**: Showed same as Total Score (e.g., 248)

### After
- **Total Score**: Shows maximum possible points based on role counts (e.g., 40 for 1×TT, 480 for 1×SMT = 520 total)
- **Obtained Score**: Shows actual earned points (e.g., 37 + 211 = 248)

## Example
If Adam Dalferes performed:
- TM role 1 time (scored 37/40)
- SMT role 1 time (scored 211/480)

**Total Score Row**: 
- TM: 1 × 40 = 40 (max possible)
- SMT: 1 × 480 = 480 (max possible)
- TOTAL: 520 (max possible)

**Obtained Score Row**:
- TM: 37 (actual)
- SMT: 211 (actual)  
- TOTAL: 248 (actual)

**Performance**: 248/520 = 47.7%

## Files Modified
1. `/backend/app/api/routes/reports.py` - Added `role_counts` tracking
2. `/frontend/src/pages/Reports.tsx` - Updated UI to use counts for max calculation

## Testing
The backend runs with `--reload`, so changes are automatically applied. Test by:
1. Navigate to the Reports page
2. Verify "Total Score" row shows maximum possible points
3. Verify "Obtained Score" row shows actual earned points
4. Compare with exported CSV/Excel to ensure consistency
