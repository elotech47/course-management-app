# Course Management System

A comprehensive digital grading system for lab courses, built with FastAPI (backend) and React (frontend).

## Features

- **User Management**: Teacher/TA registration and authentication
- **Course Management**: Create and manage multiple courses
- **Student Management**: Add students via manual entry or bulk import
- **Session Scheduling**: Create weekly class sessions
- **Role Assignment**: Assign roles (TT, TM, Camera, SMT, Lead, Reporter) to students each week
- **Digital Rubrics**: Pre-configured grading rubrics for each role:
  - Table Topic (TT): 40 points
  - Toastmaster (TM): 40 points
  - Camera Assistant: 40 points
  - Six Minute Talk (SMT): 240 points
  - Group Lead: 200 points
  - Group Reporter: 200 points
- **Grading Workspace**: Grade students with auto-loaded rubrics
- **Email Notifications**: Send graded rubrics to students via email
- **Reports & Export**: Generate grade sheets and export to CSV/Excel
- **Analytics**: View student performance and role-based statistics

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database
- **SQLAlchemy**: ORM
- **JWT**: Authentication
- **SendGrid**: Email service
- **Pandas**: Data export

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client
- **Zustand**: State management
- **TanStack Query**: Server state

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- SendGrid API key (for email functionality)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd course-management-app
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# - Set DATABASE_URL to your PostgreSQL connection string
# - Set SECRET_KEY to a secure random string
# - Set SENDGRID_API_KEY (optional, for email functionality)

# Run migrations (create tables)
python -c "from app.db import models; from app.db.database import engine; models.Base.metadata.create_all(bind=engine)"

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### First Time Setup

1. **Register an Account**
   - Navigate to `http://localhost:3000/register`
   - Create your instructor/TA account

2. **Create a Course**
   - Login and create your first course
   - Enter course code (e.g., "ME 4611"), name, section, and semester

3. **Add Students**
   - Navigate to your course
   - Add students individually or bulk import via CSV

4. **Create Class Sessions**
   - Add weekly class sessions with dates and titles

5. **Assign Roles**
   - For each session, assign roles to students
   - Available roles: TT, TM, Camera, SMT, Lead, Reporter

6. **Initialize Rubrics** (automatic on first use)
   - Rubrics are automatically created when needed
   - Or manually initialize via: `POST /api/rubrics/init-defaults`

### Grading Workflow

1. **Navigate to Session**
   - Go to course → sessions → select a session

2. **Grade Students**
   - Click "Grade Session"
   - Select a student from the list
   - The appropriate rubric auto-loads based on their role
   - Enter scores for each criterion
   - Apply deductions if needed
   - Add comments
   - Save or Save & Email

3. **Send Graded Rubrics**
   - Option 1: Send individually when grading (Save & Email)
   - Option 2: Bulk send all grades for a session

4. **View Reports**
   - Navigate to Reports section
   - View comprehensive grade summaries
   - Export to CSV or Excel

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Courses
- `POST /api/courses/` - Create course
- `GET /api/courses/` - List user's courses
- `GET /api/courses/{id}` - Get course details
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course

### Students
- `POST /api/students/` - Add student
- `POST /api/students/bulk` - Bulk import students
- `GET /api/students/course/{course_id}` - List course students
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student

### Sessions
- `POST /api/sessions/` - Create session
- `GET /api/sessions/course/{course_id}` - List course sessions
- `GET /api/sessions/{id}` - Get session details
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `POST /api/sessions/{id}/assignments` - Assign roles
- `GET /api/sessions/{id}/assignments` - Get role assignments

### Rubrics
- `GET /api/rubrics/` - List all rubrics
- `GET /api/rubrics/{role}` - Get rubric for specific role
- `POST /api/rubrics/init-defaults` - Initialize default rubrics

### Grading
- `POST /api/grading/` - Create grade record
- `GET /api/grading/session/{session_id}` - Get session grades
- `GET /api/grading/student/{student_id}` - Get student grades
- `GET /api/grading/{id}` - Get grade details
- `PUT /api/grading/{id}` - Update grade
- `DELETE /api/grading/{id}` - Delete grade
- `POST /api/grading/{id}/send-email` - Send grade email
- `POST /api/grading/session/{id}/send-all-emails` - Bulk send emails

### Reports
- `GET /api/reports/course/{id}/summary` - Course grade summary
- `GET /api/reports/student/{id}/summary` - Student summary
- `GET /api/reports/course/{id}/role-stats` - Role statistics

### Exports
- `GET /api/exports/course/{id}/grades.csv` - Export as CSV
- `GET /api/exports/course/{id}/grades.xlsx` - Export as Excel
- `GET /api/exports/student/{id}/report` - Student report

## Database Schema

Key entities:
- **User**: Instructors and TAs
- **Course**: Lab courses
- **Student**: Students enrolled in courses
- **ClassSession**: Weekly class meetings
- **RoleAssignment**: Student roles per session
- **RubricTemplate**: Grading rubrics for each role
- **GradeRecord**: Grading results with rubric snapshots
- **EmailLog**: Email delivery tracking

## Configuration

### Environment Variables

**Backend (.env)**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/course_management
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Course Management System
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
DEBUG=True
```

**Frontend (.env)**:
```
VITE_API_URL=http://localhost:8000
```

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production

**Backend**:
```bash
# Use production WSGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend**:
```bash
npm run build
# Serve the dist/ folder with nginx or similar
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `createdb course_management`

### Email Not Sending
- Verify SENDGRID_API_KEY is set
- Check SendGrid dashboard for API key permissions
- In development, emails are logged instead of sent

### CORS Errors
- Ensure backend CORS middleware includes frontend URL
- Check that API requests use correct base URL

## Future Enhancements

- Student portal (view own grades)
- Auto-rotation of role assignments
- PDF generation for rubrics
- Multi-section support
- Grade distribution analytics
- Attendance tracking
- Mobile responsive improvements

## License

MIT License

## Support

For questions or issues, please open an issue on GitHub or contact your administrator.
