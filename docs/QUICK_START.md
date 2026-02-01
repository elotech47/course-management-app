# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Git installed (optional)

## 5-Minute Setup

### Step 1: Database Setup

Create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE course_management;

# Create user (optional)
CREATE USER course_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE course_management TO course_admin;

\q
```

### Step 2: Run Setup Script

**On macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

### Step 3: Configure Backend

Edit `backend/.env`:

```bash
# Minimum required configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/course_management
SECRET_KEY=your-secret-random-string-here-make-it-long

# Optional (for email functionality)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

### Step 4: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Access the Application

1. Open browser to `http://localhost:3000`
2. Click "Sign Up" and create your account
3. Start using the system!

## Common Tasks

### Add Your First Course

1. Login to the dashboard
2. Click "New Course"
3. Fill in:
   - Course Code: "ME 4611"
   - Course Name: "Engineering Lab"
   - Section: "Section 1"
   - Semester: "Fall 2025"
4. Click "Create"

### Add Students

**Option 1: Manual Entry**
1. Go to your course
2. Click "Students" tab
3. Click "Add Student"
4. Enter name and email

**Option 2: Bulk Import (Coming Soon)**
Prepare CSV file with columns: `full_name`, `email`, `student_id`

### Create a Class Session

1. Go to your course
2. Click "Sessions" tab
3. Click "Add Session"
4. Fill in:
   - Session Number: 1
   - Date: Select date
   - Title: "Introduction" or "Exp 1"

### Assign Roles to Students

1. Go to session
2. Click "Assign Roles"
3. For each student, select their role:
   - TT (Table Topic) - 40 pts
   - TM (Toastmaster) - 40 pts
   - Camera (Camera Assistant) - 40 pts
   - SMT (Six Minute Talk) - 240 pts
   - Lead (Group Lead) - 200 pts
   - Reporter (Group Reporter) - 200 pts

### Grade a Session

1. Navigate to session
2. Click "Grade Session"
3. Select student from left panel
4. Rubric loads automatically
5. Enter scores for each criterion
6. Add any deductions
7. Write comments
8. Click "Save & Email" to save and notify student

### Export Grades

1. Go to course "Reports" section
2. Click "Export CSV" or "Export Excel"
3. File downloads automatically

## Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError`**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error: Database connection failed**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Test connection: `psql -U postgres -d course_management`

### Frontend won't start

**Error: `Cannot find module`**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error: API requests fail**
- Ensure backend is running on port 8000
- Check VITE_API_URL in frontend/.env
- Check browser console for CORS errors

### Emails not sending

- Emails are optional for development
- To enable emails:
  1. Sign up for SendGrid (free tier available)
  2. Get API key from SendGrid dashboard
  3. Add to backend/.env: `SENDGRID_API_KEY=your_key`
  4. Restart backend server

## Default Rubrics

The system comes with pre-configured rubrics for all roles:

### Table Topic (TT) - 40 points
- Presentation Quality: 0-10
- Content & Organization: 0-10
- Delivery & Confidence: 0-10
- Audience Engagement: 0-10

### Toastmaster (TM) - 40 points
- Moderation Skills: 0-10
- Time Management: 0-10
- Introductions & Transitions: 0-10
- Feedback Quality: 0-10

### Camera Assistant - 40 points
- Video Quality & Framing: 0-14
- Audio Quality: 0-12
- Professionalism & Timing: 0-14

### Six Minute Talk (SMT) - 240 points
- Organization & Structure: 0-40
- Content Quality: 0-40
- Visual Aids: 0-40
- Delivery & Presence: 0-40
- Technical Accuracy: 0-40
- Time Management: 0-40

### Group Lead - 200 points
- Leadership & Coordination: 0-40
- Planning & Preparation: 0-40
- Task Delegation: 0-30
- Communication: 0-30
- Problem Solving: 0-30
- Team Support: 0-30

### Group Reporter - 200 points
- Report Quality: 0-50
- Data Analysis: 0-40
- Documentation: 0-40
- Presentation of Findings: 0-35
- Team Collaboration: 0-35

## Tips for Success

1. **Start Small**: Begin with one course and a few students
2. **Grade Regularly**: Grade sessions soon after they occur
3. **Use Comments**: Provide meaningful feedback in comments
4. **Backup Data**: Regularly export grades to Excel
5. **Test Emails**: Send test email to yourself first
6. **Plan Ahead**: Create all sessions at the start of semester

## Getting Help

- Check README.md for detailed documentation
- Review API documentation at `http://localhost:8000/docs`
- Check browser console for frontend errors
- Check terminal output for backend errors

## Next Steps

Once comfortable with basics:
- Explore the Reports section
- Try exporting to Excel
- Set up email notifications
- Add more courses and students
- Customize rubrics (advanced)

Happy grading! 🎓
