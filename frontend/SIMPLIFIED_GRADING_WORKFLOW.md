# Simplified Grading Workflow - Role Assignment on Demand

## Overview
Removed the separate "Assign Roles" step and integrated role assignment directly into the grading workflow. Teachers can now grade students immediately without pre-assigning roles, and the system prompts for role selection when needed.

## Changes Made

### 1. GradingWorkspace Component (`frontend/src/pages/GradingWorkspace.tsx`)

#### Added New Interfaces
```typescript
interface Assignment {
  id: number
  student_id: number
  student_name: string
  role: string | null  // Now nullable
}

interface Student {
  id: number
  full_name: string
  email: string
  student_id: string
}
```

#### New State Management
- **`students`**: All students in the course
- **`showRoleModal`**: Controls role selection modal visibility
- **`selectedRole`**: Stores the role being assigned

#### Updated Logic

**`loadStudentsAndAssignments()`**:
```typescript
// Load all students from the course
const studentsResponse = await api.get(`/api/students/course/${courseId}`)

// Load existing role assignments
const assignmentsResponse = await api.get(`/api/sessions/${sessionId}/assignments`)

// Create combined list: students with their roles (or null if unassigned)
const combinedList: Assignment[] = students.map(student => ({
  ...student,
  role: assignmentMap.get(student.id) || null
}))
```

**`handleStudentSelect()`**:
```typescript
// If student has no role, show role selection modal
if (!assignment.role) {
  setSelectedStudent(assignment)
  setShowRoleModal(true)
} else {
  setSelectedStudent(assignment)
  // Proceed to load rubric
}
```

**`handleRoleSelection()`**:
```typescript
// Save role assignment via API
await api.post(`/api/sessions/${sessionId}/assignments`, [{
  student_id: selectedStudent.student_id,
  role: selectedRole
}])

// Update local state
setAssignments(prevAssignments => 
  prevAssignments.map(a => 
    a.student_id === selectedStudent.student_id 
      ? { ...a, role: selectedRole } 
      : a
  )
)

// Load rubric for the newly assigned role
loadRubricAndGrade(selectedRole, selectedStudent.student_id)
```

#### UI Updates

**Student List**:
- Shows all students in the course
- Displays role if assigned
- Shows "⚠️ No role assigned" if no role

```typescript
<div className="text-xs text-gray-500">
  {assignment.role ? assignment.role : '⚠️ No role assigned'}
</div>
```

**Grading Area**:
- Shows grading form if student has role
- Shows message if no role assigned:
  - "Please assign a role to this student to begin grading."
  - "Select a student to begin grading"

**Role Selection Modal**:
- Opens when clicking a student without a role
- Shows all available roles with point values
- Visual selection with checkmarks
- "Assign Role" button saves and proceeds to grading

### 2. CourseDetail Component (`frontend/src/pages/CourseDetail.tsx`)

#### Removed Features
- ❌ "Assign Roles" button from session cards
- ❌ Role Assignment modal
- ❌ `showRoleAssignmentModal` state
- ❌ `selectedSessionId` state
- ❌ `roleAssignments` state
- ❌ `handleAssignRoles()` function
- ❌ `handleSaveRoleAssignments()` function

#### Simplified Session Card
```typescript
<div className="flex space-x-2">
  <Link to={`/grading/${session.id}`}>
    Grade Session
  </Link>
  <button onClick={() => handleDeleteSessionClick(session)}>
    Delete
  </button>
</div>
```

## User Workflow

### Before (Old Workflow)
1. Create session
2. Click "Assign Roles" ✋ **Required step**
3. Assign roles to all students in modal
4. Save role assignments
5. Click "Grade Session"
6. Select student to grade

### After (New Workflow)
1. Create session
2. Click "Grade Session" ✅ **Direct access**
3. See all students (with or without roles)
4. Click student to grade
5. If no role → **Role selection modal appears**
6. Assign role → Immediately proceed to grading

## Benefits

### 1. **Flexibility**
- Grade students in any order
- Don't need to assign all roles upfront
- Can assign roles on-the-fly

### 2. **Simplicity**
- One less step in the workflow
- No separate "Assign Roles" page
- Integrated experience

### 3. **Efficiency**
- Immediate grading access
- Assign role only when needed
- Less clicking and navigation

### 4. **Better UX**
- Clear visual indicators (⚠️ No role assigned)
- Automatic prompting when needed
- Seamless role assignment within grading flow

## Technical Details

### API Endpoints Used
- **GET** `/api/students/course/{course_id}` - Load all students
- **GET** `/api/sessions/{session_id}/assignments` - Load existing role assignments
- **POST** `/api/sessions/{session_id}/assignments` - Save role assignment (single student)
- **GET** `/api/rubrics/{role}` - Load rubric for assigned role

### State Management
```typescript
// GradingWorkspace now maintains:
- students: Student[]              // All students in course
- assignments: Assignment[]         // Students with role status
- showRoleModal: boolean           // Role selection visibility
- selectedRole: string             // Currently selecting role
```

### Role Assignment Storage
Role assignments are still stored in the database via the same backend endpoint:
```python
POST /api/sessions/{session_id}/assignments
Body: [{ "student_id": 1, "role": "TT" }]
```

The difference is that assignments can be created one at a time during grading, rather than all at once before grading.

## Edge Cases Handled

✅ **Student with no role**: Shows modal to assign role  
✅ **Student with existing role**: Loads rubric immediately  
✅ **Changing roles**: Can reassign by clicking student  
✅ **Empty student list**: Shows "No students" message  
✅ **Cancel role selection**: Returns to student list without selection

## Backward Compatibility

- ✅ Existing role assignments still work
- ✅ Backend API unchanged
- ✅ Database schema unchanged
- ✅ Reports still show roles correctly

## Future Enhancements

Potential improvements:
1. **Bulk Role Assignment**: Optional button to assign all at once
2. **Role History**: Track role changes over time
3. **Role Conflicts**: Warn if multiple students have same role
4. **Role Suggestions**: Auto-suggest roles based on history
5. **Quick Role Change**: Edit role without reopening modal

## Testing Checklist

- [ ] Open grading workspace for new session
- [ ] Verify all students shown in list
- [ ] Click student without role
- [ ] Verify role selection modal appears
- [ ] Select a role and confirm
- [ ] Verify role is saved
- [ ] Verify rubric loads correctly
- [ ] Verify grading works normally
- [ ] Click student with existing role
- [ ] Verify direct access to grading form
- [ ] Verify "Assign Roles" button removed from course detail
- [ ] Verify session stats still show correctly
