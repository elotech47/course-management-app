# Course Management System - Project Overview

## 🎯 What We Built

A complete digital grading system for LAB courses that replaces manual paper-based rubric grading with a streamlined web application.

## 📁 Project Structure

```
course-management-app/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/     # API endpoints
│   │   │       ├── auth.py         # Authentication
│   │   │       ├── courses.py      # Course management
│   │   │       ├── students.py     # Student management
│   │   │       ├── sessions.py     # Class sessions & roles
│   │   │       ├── rubrics.py      # Rubric templates
│   │   │       ├── grading.py      # Grading functionality
│   │   │       ├── reports.py      # Analytics & reports
│   │   │       └── exports.py      # CSV/Excel exports
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   └── security.py        # Auth & JWT
│   │   ├── db/
│   │   │   ├── database.py        # Database connection
│   │   │   └── models.py          # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic
│   │   │   ├── email_service.py   # Email sending
│   │   │   └── email_template.py  # Email templates
│   │   └── main.py               # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.tsx         # Main layout
│   │   ├── pages/
│   │   │   ├── Login.tsx          # Login page
│   │   │   ├── Register.tsx       # Registration
│   │   │   ├── Dashboard.tsx      # Course list
│   │   │   ├── CourseDetail.tsx   # Course management
│   │   │   ├── GradingWorkspace.tsx # Main grading UI
│   │   │   ├── StudentDetail.tsx  # Student profile
│   │   │   └── Reports.tsx        # Reports & exports
│   │   ├── store/
│   │   │   └── authStore.ts       # Auth state
│   │   ├── lib/
│   │   │   └── api.ts             # Axios client
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── README.md              # Full documentation
├── QUICK_START.md         # Quick setup guide
├── setup.sh              # Linux/Mac setup script
├── setup.bat             # Windows setup script
├── start.sh              # Start both servers (Unix)
├── start.bat             # Start both servers (Windows)
├── docker-compose.yml    # Docker setup
└── .gitignore

```

## ⚡ Key Features Implemented

### 1. **Authentication System**
- User registration and login
- JWT-based authentication
- Role-based access (Instructor/TA)

### 2. **Course Management**
- Create multiple courses
- Course information (code, name, section, semester)
- Student roster management
- Bulk student import capability

### 3. **Session Scheduling**
- Weekly class sessions
- Session metadata (date, title, experiment)
- Track grading progress per session

### 4. **Role Assignment**
- Assign roles to students each week
- 6 role types with different point values:
  - **TT** (Table Topic): 40 points
  - **TM** (Toastmaster): 40 points
  - **Camera** (Camera Assistant): 40 points
  - **SMT** (Six Minute Talk): 240 points
  - **Lead** (Group Lead): 200 points
  - **Reporter** (Group Reporter): 200 points

### 5. **Digital Rubrics**
- Pre-configured rubrics for each role
- Criteria with scoring scales
- Deduction system
- Automatic score calculation
- Rubric snapshots for historical accuracy

### 6. **Grading Workspace**
- Clean UI for grading students
- Auto-loads appropriate rubric based on role
- Slider inputs for scoring
- Checkbox deductions
- Comments section
- Real-time score calculation
- "Save & Email" functionality

### 7. **Email Notifications**
- Beautifully formatted HTML emails
- Contains full graded rubric
- Criterion breakdown
- Deductions and comments
- SendGrid integration
- Bulk email capability

### 8. **Reports & Analytics**
- Course-wide grade summaries
- Individual student reports
- Role-based statistics
- Performance tracking

### 9. **Export Functionality**
- CSV export (Excel-compatible)
- XLSX export with formatting
- Individual student reports
- Matches your original grade sheet format

## 🏗️ Architecture

### Backend (FastAPI)
- **REST API** with automatic OpenAPI docs
- **PostgreSQL** database for data persistence
- **SQLAlchemy ORM** for database operations
- **JWT authentication** for security
- **Pydantic** for data validation
- **Pandas** for data export
- **SendGrid** for email delivery

### Frontend (React)
- **React 18** with TypeScript
- **Vite** for fast development
- **TailwindCSS** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Axios** for API calls
- **React Query** for server state (configured)

## 🔄 Workflow

### For Teachers/TAs:

1. **Setup** → Register account → Create course → Add students
2. **Schedule** → Create sessions → Assign roles to students
3. **Grade** → Open grading workspace → Select student → Enter scores → Save
4. **Notify** → Send email with graded rubric to student
5. **Report** → View analytics → Export grade sheets

### For Students (via email):
- Receive beautifully formatted graded rubric
- See all scores and deductions
- Read instructor comments
- Track progress throughout semester

## 📊 Database Schema

**Key Entities:**
- `users` - Teachers/TAs
- `courses` - Lab courses
- `students` - Enrolled students
- `class_sessions` - Weekly meetings
- `role_assignments` - Student roles per session
- `rubric_templates` - Grading rubrics
- `grade_records` - Grades with snapshots
- `email_logs` - Email delivery tracking

## 🚀 Getting Started

**Fastest way:**
```bash
# Run setup script
./setup.sh

# Edit configuration
nano backend/.env

# Start everything
./start.sh
```

**Manual way:** See README.md for detailed instructions.

## 🎨 UI Highlights

- **Clean, modern design** with Tailwind CSS
- **Responsive layout** works on all screen sizes
- **Intuitive navigation** with clear visual hierarchy
- **Color-coded elements** for easy scanning
- **Loading states** and error handling
- **Form validation** for data integrity

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Protected API endpoints
- SQL injection prevention (ORM)
- CORS configuration
- Input validation

## 📈 Scalability

- Supports multiple courses
- Unlimited students per course
- Unlimited sessions per course
- Historical grade tracking
- Rubric versioning
- Email queuing ready (Celery integration prepared)

## 🛠️ Customization Options

### Easy to Modify:
- Rubric criteria and points
- Role types and names
- Email templates
- UI colors and branding
- Export formats

### Extensible:
- Add new role types
- Create custom rubrics
- Implement auto-role-rotation
- Add student portal
- Integrate with LMS

## 📦 What's Included

### Documentation:
- ✅ README.md - Complete documentation
- ✅ QUICK_START.md - 5-minute setup guide
- ✅ Inline code comments
- ✅ API documentation (auto-generated at /docs)

### Scripts:
- ✅ setup.sh / setup.bat - Automated setup
- ✅ start.sh / start.bat - Start servers
- ✅ Docker configuration

### Code:
- ✅ Complete backend API (FastAPI)
- ✅ Complete frontend (React + TypeScript)
- ✅ Database models and migrations
- ✅ Authentication system
- ✅ Email service
- ✅ Export functionality

## 🎓 Based on Your Requirements

This system digitizes your exact workflow:

✅ **Your current process:** Print rubric → Grade manually → Email results  
✅ **New process:** Open grading workspace → Enter scores → Click "Save & Email"

✅ **Your rubrics:** All 6 roles (TT, TM, Camera, SMT, Lead, Reporter)  
✅ **Your schedule:** Weekly sessions with role assignments  
✅ **Your grade sheet:** Exported to Excel matching your format  

## 🔮 Future Enhancements (Not Implemented)

- Student self-service portal
- Mobile app
- Automatic role rotation algorithm
- PDF generation for certificates
- Integration with university LMS
- Real-time collaboration
- Advanced analytics dashboard
- Attendance tracking

## 💡 Tips for Usage

1. **Start small**: Test with one course and a few students
2. **Grade regularly**: Don't let grading pile up
3. **Use comments**: Students appreciate detailed feedback
4. **Export often**: Regular backups of grade data
5. **Test emails**: Send yourself a test before emailing students

## 🐛 Known Limitations

- Email requires SendGrid account (optional for development)
- Bulk CSV import UI not yet implemented (API ready)
- Student portal not included in this version
- Single instructor per course (can be extended)

## 📞 Support

- Check documentation in README.md and QUICK_START.md
- API docs available at http://localhost:8000/docs
- Code is fully commented for easy understanding
- Database schema is well-structured for modifications

---

**You now have a production-ready course management system that will save you hours of manual grading work each week!** 🎉

The system is fully functional and ready to use for your upcoming semester. Just follow the QUICK_START.md guide to get it running.
