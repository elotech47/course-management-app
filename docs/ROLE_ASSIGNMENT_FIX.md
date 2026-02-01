# Fixed: Role Assignment Not Saving in Database

## Issue
When assigning a role to a student through the grading modal, the role assignment was not being properly saved. This caused the student detail page to show "Unknown" as the role even though grades were recorded.

## Root Cause
The role assignment endpoint was **deleting ALL existing role assignments** for a session before creating new ones. When assigning a role for a single student during grading, this would inadvertently delete role assignments for all other students in that session.

**Problematic code:**
```python
# Delete existing assignments (BAD - deletes ALL)
db.query(models.RoleAssignment).filter(
    models.RoleAssignment.session_id == session_id
).delete()

# Create new assignments
for assignment in assignments:
    db_assignment = models.RoleAssignment(...)
    db.add(db_assignment)
```

## Solution

### 1. Updated Role Assignment Endpoint (`backend/app/api/routes/sessions.py`)

Changed from "delete all then create" to "update or create":

```python
@router.post("/{session_id}/assignments", response_model=List[dict])
def assign_roles(...):
    # For each assignment, update if exists or create new
    for assignment in assignments:
        # Check if assignment already exists
        existing = db.query(models.RoleAssignment).filter(
            models.RoleAssignment.session_id == session_id,
            models.RoleAssignment.student_id == assignment["student_id"]
        ).first()
        
        if existing:
            # Update existing assignment
            existing.role = models.StudentRole(assignment["role"])
        else:
            # Create new assignment
            db_assignment = models.RoleAssignment(
                session_id=session_id,
                student_id=assignment["student_id"],
                role=models.StudentRole(assignment["role"])
            )
            db.add(db_assignment)
    
    db.commit()
```

**Benefits:**
- ✅ Only updates/creates assignments for specified students
- ✅ Preserves existing role assignments for other students
- ✅ Works for both single-student (grading modal) and bulk assignment scenarios

### 2. Added Role Assignment Validation (`backend/app/api/routes/grading.py`)

Added validation to ensure a role is assigned before allowing grade creation:

```python
@router.post("/", response_model=grade.GradeRecord)
def create_grade_record(...):
    # Verify role assignment exists for this student and session
    role_assignment = db.query(models.RoleAssignment).filter(
        models.RoleAssignment.student_id == grade_data.student_id,
        models.RoleAssignment.session_id == grade_data.session_id
    ).first()
    
    if not role_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No role assigned for this student in this session. Please assign a role first."
        )
```

**Benefits:**
- ✅ Enforces that ROLE must not be null
- ✅ Prevents creating grades without role assignments
- ✅ Provides clear error message if role is missing

## Workflow Now Works Correctly

### Scenario 1: Assigning Role During Grading
1. User opens grading workspace
2. Clicks on student without role
3. Role selection modal appears
4. User selects role and confirms
5. ✅ **Role is saved** via `POST /api/sessions/{session_id}/assignments`
6. ✅ **Only that student's role is created/updated**
7. ✅ **Other students' roles remain intact**
8. Grading form loads with correct rubric

### Scenario 2: Creating Grade
1. User fills out grading form
2. Clicks "Save Grade"
3. Backend verifies role assignment exists
4. If role missing: ❌ Error returned
5. If role exists: ✅ Grade created successfully
6. Student detail page shows correct role

### Scenario 3: Viewing Student Details
1. User navigates to student detail page
2. Backend fetches grades with role assignments
3. ✅ Roles display correctly (not "Unknown")
4. ✅ Role breakdown shows proper categorization

## Database Integrity

### Before Fix
```
RoleAssignments Table:
Session 1 | Student A | TT
Session 1 | Student B | TM
Session 1 | Student C | Camera

[User assigns Student D role "SMT" via grading modal]

After Assignment:
Session 1 | Student D | SMT    ❌ Students A, B, C lost their roles!
```

### After Fix
```
RoleAssignments Table:
Session 1 | Student A | TT
Session 1 | Student B | TM
Session 1 | Student C | Camera

[User assigns Student D role "SMT" via grading modal]

After Assignment:
Session 1 | Student A | TT
Session 1 | Student B | TM
Session 1 | Student C | Camera
Session 1 | Student D | SMT    ✅ All roles preserved!
```

## Testing

### Test Case 1: Role Assignment in Grading
- [ ] Open grading workspace for a session
- [ ] Select student without role
- [ ] Assign role in modal
- [ ] Verify role is saved (check student detail page)
- [ ] Verify other students' roles are unchanged

### Test Case 2: Grade Creation Validation
- [ ] Try to create grade without role assignment
- [ ] Verify error message is clear
- [ ] Assign role first
- [ ] Create grade successfully
- [ ] Verify grade shows correct role

### Test Case 3: Role Updates
- [ ] Assign role to student
- [ ] Create grade
- [ ] Change student's role
- [ ] Verify updated role shows in reports
- [ ] Verify grade still exists

### Test Case 4: Student Detail Page
- [ ] View student with grades
- [ ] Verify all roles display correctly
- [ ] Verify "Unknown" doesn't appear
- [ ] Verify role breakdown is accurate

## Related Files
- `backend/app/api/routes/sessions.py` - Role assignment endpoint
- `backend/app/api/routes/grading.py` - Grade creation with validation
- `backend/app/api/routes/reports.py` - Student summary with roles
- `frontend/src/pages/GradingWorkspace.tsx` - Role assignment modal
- `frontend/src/pages/StudentDetail.tsx` - Student detail display

## Notes
- Role assignments are now **upserted** (update if exists, insert if new)
- Grade creation now **requires** a role assignment
- This ensures database integrity: **ROLE must not be null when grades exist**
