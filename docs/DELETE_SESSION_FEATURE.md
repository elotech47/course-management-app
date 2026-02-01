# Delete Session Feature

## Overview
Added the ability to delete class sessions with a confirmation dialog to prevent accidental deletions.

## Changes Made

### Backend (`backend/app/api/routes/sessions.py`)

Updated the `DELETE /api/sessions/{session_id}` endpoint to properly cascade delete all related data:

```python
@router.delete("/{session_id}")
def delete_session(session_id: int, ...):
    # Check access permissions
    check_course_access(db_session.course_id, current_user.id, db)
    
    # Delete all related data in correct order:
    # 1. Delete grade records (reference role assignments)
    db.query(models.GradeRecord).filter(
        models.GradeRecord.session_id == session_id
    ).delete()
    
    # 2. Delete role assignments
    db.query(models.RoleAssignment).filter(
        models.RoleAssignment.session_id == session_id
    ).delete()
    
    # 3. Delete the session itself
    db.delete(db_session)
    db.commit()
```

### Frontend (`frontend/src/pages/CourseDetail.tsx`)

#### 1. Added Delete Button
- Added a "Delete" button with trash icon to each session card
- Button styled in red to indicate destructive action
- Positioned alongside "Assign Roles" and "Grade Session" buttons

#### 2. Added State Management
```typescript
const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false)
const [sessionToDelete, setSessionToDelete] = useState<Session | null>(null)
```

#### 3. Added Handler Functions
```typescript
const handleDeleteSessionClick = (session: Session) => {
  setSessionToDelete(session)
  setShowDeleteConfirmModal(true)
}

const handleConfirmDelete = async () => {
  // Call API to delete session
  await api.delete(`/api/sessions/${sessionToDelete.id}`)
  // Reload course data
  loadCourseData()
  toast.success('Session deleted successfully!', { icon: '🗑️' })
}

const handleCancelDelete = () => {
  setShowDeleteConfirmModal(false)
  setSessionToDelete(null)
}
```

#### 4. Added Confirmation Modal
Created a comprehensive confirmation modal that shows:
- ⚠️ Warning icon in red circular background
- Session name being deleted
- List of what will be deleted:
  - Number of role assignments
  - Number of grade records
  - The session itself
- Clear warning that action cannot be undone
- Two action buttons:
  - "Cancel" (gray) - to abort deletion
  - "Delete Session" (red) - to confirm deletion

## UI/UX Features

### Visual Hierarchy
1. **Delete Button**: Red border and text to indicate danger
2. **Modal**: Prominent warning icon and clear messaging
3. **Information Display**: Shows exactly what data will be lost
4. **Action Buttons**: Color-coded for clarity (gray = safe, red = danger)

### User Flow
1. User clicks "Delete" button on session card
2. Confirmation modal appears with session details
3. Modal shows:
   - Session name and number
   - Count of assignments to be deleted
   - Count of grades to be deleted
   - Warning about permanent deletion
4. User can:
   - Click "Cancel" to abort (modal closes)
   - Click "Delete Session" to confirm (deletes and shows success toast)

### Safety Features
- ✅ **Confirmation Required**: Two-step process prevents accidental deletion
- ✅ **Clear Information**: Shows exactly what will be deleted
- ✅ **Visual Warnings**: Red colors and warning icon
- ✅ **Explicit Text**: "This action cannot be undone!"
- ✅ **Permission Check**: Backend validates user has access to course

## Data Cascade Deletion

When a session is deleted, the following occurs **in order**:

1. **Grade Records** (`GradeRecord` table)
   - All grades for the session are deleted
   - Includes rubric snapshots and criterion scores
   
2. **Role Assignments** (`RoleAssignment` table)
   - All role assignments for the session are deleted
   
3. **Session** (`ClassSession` table)
   - The session itself is deleted

## Testing Checklist

- [ ] Delete button appears on each session card
- [ ] Clicking delete button opens confirmation modal
- [ ] Modal displays correct session information
- [ ] Modal shows correct counts for assignments and grades
- [ ] "Cancel" button closes modal without deleting
- [ ] "Delete Session" button successfully deletes session
- [ ] Success toast appears after deletion
- [ ] Session list refreshes and deleted session is gone
- [ ] Error handling works if deletion fails
- [ ] Backend properly deletes all related data
- [ ] Backend checks user permissions before deletion

## Error Handling

- **Session Not Found**: Returns 404 error
- **No Permission**: Returns 403 error (from `check_course_access`)
- **Database Error**: Catches and displays error message
- **Network Error**: Shows toast notification with error

## Future Enhancements

Potential improvements:
1. **Soft Delete**: Keep session but mark as deleted
2. **Undo Feature**: Allow restoration within time window
3. **Archive**: Move to archived sessions instead of deleting
4. **Bulk Delete**: Delete multiple sessions at once
5. **Export Before Delete**: Automatically backup session data
6. **Confirmation Code**: Require typing session name to confirm

## Related Files

- `backend/app/api/routes/sessions.py` - Backend deletion logic
- `frontend/src/pages/CourseDetail.tsx` - Frontend UI and handlers
- `backend/app/db/models.py` - Database models with relationships
