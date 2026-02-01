import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Plus, Users, Calendar, FileText, Upload, Trash2 } from 'lucide-react'
import toast, { Toaster } from 'react-hot-toast'
import api from '@/lib/api'

interface Course {
  id: number
  name: string
  code: string
  section: string
  semester: string
}

interface Student {
  id: number
  full_name: string
  email: string
  student_id: string
}

interface Session {
  id: number
  session_number: number
  session_date: string
  title: string
  assignment_count: number
  graded_count: number
}

export default function CourseDetail() {
  const { courseId } = useParams()
  const [course, setCourse] = useState<Course | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeTab, setActiveTab] = useState<'students' | 'sessions'>('students')
  const [loading, setLoading] = useState(true)
  const [showAddStudentModal, setShowAddStudentModal] = useState(false)
  const [showAddSessionModal, setShowAddSessionModal] = useState(false)
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false)
  const [sessionToDelete, setSessionToDelete] = useState<Session | null>(null)
  const [newStudent, setNewStudent] = useState({
    full_name: '',
    email: '',
    student_id: '',
  })
  const [newSession, setNewSession] = useState({
    session_number: 1,
    session_date: '',
    title: '',
    experiment_title: '',
  })

  useEffect(() => {
    loadCourseData()
  }, [courseId])

  const loadCourseData = async () => {
    try {
      const [courseRes, studentsRes, sessionsRes] = await Promise.all([
        api.get(`/api/courses/${courseId}`),
        api.get(`/api/students/course/${courseId}`),
        api.get(`/api/sessions/course/${courseId}`),
      ])
      
      setCourse(courseRes.data)
      setStudents(studentsRes.data)
      setSessions(sessionsRes.data)
    } catch (error) {
      console.error('Failed to load course data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/api/students/', {
        ...newStudent,
        course_id: Number(courseId),
      })
      setShowAddStudentModal(false)
      setNewStudent({ full_name: '', email: '', student_id: '' })
      loadCourseData()
      toast.success('Student added successfully!', { icon: '✅' })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add student')
    }
  }

  const handleAddSession = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/api/sessions/', {
        ...newSession,
        course_id: Number(courseId),
      })
      setShowAddSessionModal(false)
      setNewSession({ session_number: 1, session_date: '', title: '', experiment_title: '' })
      loadCourseData()
      toast.success('Session added successfully!', { icon: '✅' })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add session')
    }
  }

  const handleDeleteSessionClick = (session: Session) => {
    setSessionToDelete(session)
    setShowDeleteConfirmModal(true)
  }

  const handleConfirmDelete = async () => {
    if (!sessionToDelete) return

    try {
      await api.delete(`/api/sessions/${sessionToDelete.id}`)
      setShowDeleteConfirmModal(false)
      setSessionToDelete(null)
      loadCourseData()
      toast.success('Session deleted successfully!', { icon: '🗑️' })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete session')
    }
  }

  const handleCancelDelete = () => {
    setShowDeleteConfirmModal(false)
    setSessionToDelete(null)
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!course) {
    return <div className="text-center py-12">Course not found</div>
  }

  return (
    <div>
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="mb-8">
        <Link to="/dashboard" className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Dashboard
        </Link>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{course.code}</h1>
            <p className="text-lg text-gray-600 mt-1">{course.name}</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
              <span>Section: {course.section || 'N/A'}</span>
              <span>•</span>
              <span>{course.semester}</span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Link
              to={`/reports/${courseId}`}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              <FileText className="h-4 w-4" />
              <span>Reports</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('students')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition ${
              activeTab === 'students'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Users className="inline h-4 w-4 mr-2" />
            Students ({students.length})
          </button>
          <button
            onClick={() => setActiveTab('sessions')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition ${
              activeTab === 'sessions'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Calendar className="inline h-4 w-4 mr-2" />
            Sessions ({sessions.length})
          </button>
        </nav>
      </div>

      {/* Students Tab */}
      {activeTab === 'students' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Students</h2>
            <button 
              onClick={() => setShowAddStudentModal(true)}
              className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="h-4 w-4" />
              <span>Add Student</span>
            </button>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/students/${student.id}`} className="text-primary-600 hover:text-primary-700 font-medium">
                        {student.full_name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {student.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {student.student_id || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link to={`/students/${student.id}`} className="text-primary-600 hover:text-primary-700">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sessions Tab */}
      {activeTab === 'sessions' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Class Sessions</h2>
            <button 
              onClick={() => setShowAddSessionModal(true)}
              className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="h-4 w-4" />
              <span>Add Session</span>
            </button>
          </div>

          <div className="grid gap-4">
            {sessions.map((session) => (
              <div key={session.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Class {session.session_number} - {session.title || 'Session'}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(session.session_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Link
                      to={`/grading/${session.id}`}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                    >
                      Grade Session
                    </Link>
                    <button
                      onClick={() => handleDeleteSessionClick(session)}
                      className="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition flex items-center space-x-1"
                      title="Delete session"
                    >
                      <Trash2 className="h-4 w-4" />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                <div className="mt-4 flex items-center space-x-6 text-sm text-gray-600">
                  <span>{session.assignment_count} roles assigned</span>
                  <span>•</span>
                  <span>{session.graded_count} graded</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Student Modal */}
      {showAddStudentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Add Student</h2>
            
            <form onSubmit={handleAddStudent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={newStudent.full_name}
                  onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  required
                  value={newStudent.email}
                  onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Student ID (Optional)
                </label>
                <input
                  type="text"
                  value={newStudent.student_id}
                  onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="123456"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddStudentModal(false)
                    setNewStudent({ full_name: '', email: '', student_id: '' })
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                >
                  Add Student
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Session Modal */}
      {showAddSessionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Add Class Session</h2>
            
            <form onSubmit={handleAddSession} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Number *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  value={newSession.session_number}
                  onChange={(e) => setNewSession({ ...newSession, session_number: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Date *
                </label>
                <input
                  type="date"
                  required
                  value={newSession.session_date}
                  onChange={(e) => setNewSession({ ...newSession, session_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={newSession.title}
                  onChange={(e) => setNewSession({ ...newSession, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Practice, Exp 1, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experiment Title
                </label>
                <input
                  type="text"
                  value={newSession.experiment_title}
                  onChange={(e) => setNewSession({ ...newSession, experiment_title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Time Constant, Clapeyron, etc."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddSessionModal(false)
                    setNewSession({ session_number: 1, session_date: '', title: '', experiment_title: '' })
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                >
                  Add Session
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirmModal && sessionToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Delete Session</h2>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <span className="font-semibold">Class {sessionToDelete.session_number} - {sessionToDelete.title || 'Session'}</span>?
              <br /><br />
              This will permanently delete:
            </p>
            
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 mb-6 ml-2">
              <li>All role assignments ({sessionToDelete.assignment_count} assignments)</li>
              <li>All grade records ({sessionToDelete.graded_count} grades)</li>
              <li>The session itself</li>
            </ul>
            
            <p className="text-red-600 font-semibold text-sm mb-6">
              ⚠️ This action cannot be undone!
            </p>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleCancelDelete}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
              >
                Delete Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
