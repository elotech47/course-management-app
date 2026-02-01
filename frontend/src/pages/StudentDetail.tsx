import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText, TrendingUp, Download } from 'lucide-react'
import api from '@/lib/api'
import toast, { Toaster } from 'react-hot-toast'

interface Student {
  id: number
  name: string
  email: string
  student_id: string
  course_id: number
}

interface GradeDetail {
  session_number: number
  session_date: string
  session_title: string
  session_id: number
  role: string
  score: number
  max_points: number
}

interface RoleTotal {
  count: number
  total: number
  max: number
}

interface StudentSummary {
  student: Student
  summary: {
    total_score: number
    graded_sessions: number
    total_sessions: number
    completion_rate: number
  }
  role_breakdown: Record<string, RoleTotal>
  grade_details: GradeDetail[]
}

export default function StudentDetail() {
  const { studentId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<StudentSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStudentData()
  }, [studentId])

  const loadStudentData = async () => {
    try {
      const response = await api.get(`/api/reports/student/${studentId}/summary`)
      setData(response.data)
    } catch (error) {
      console.error('Failed to load student data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewReport = () => {
    navigate(`/students/${studentId}/report`)
  }

  const handleDownloadPDF = async (sessionId: number, sessionNumber: number, role: string) => {
    try {
      toast.loading('Generating PDF...')
      const response = await api.get(
        `/api/exports/student/${studentId}/session/${sessionId}/rubric.pdf`,
        { responseType: 'blob' }
      )
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${data?.student.name}_Session${sessionNumber}_${role}_Rubric.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.dismiss()
      toast.success('PDF downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to generate PDF')
      console.error('PDF download failed:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Student not found</p>
      </div>
    )
  }

  return (
    <div>
      <Toaster position="top-right" />
      <Link to={`/courses/${data.student.course_id}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Course
      </Link>

      {/* Student Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{data.student.name}</h1>
            <div className="space-y-1 text-sm text-gray-600">
              <p><span className="font-medium">Student ID:</span> {data.student.student_id}</p>
              <p><span className="font-medium">Email:</span> {data.student.email}</p>
            </div>
          </div>
          <button 
            onClick={handleViewReport}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            <FileText className="h-4 w-4" />
            <span>View Report</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {Math.round(data.summary.total_score)}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm text-gray-600">Sessions Graded</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {data.summary.graded_sessions} / {data.summary.total_sessions}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm text-gray-600">Completion Rate</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {Math.round(data.summary.completion_rate)}%
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm text-gray-600">Average Score</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {data.summary.graded_sessions > 0
                ? Math.round(data.summary.total_score / data.summary.graded_sessions)
                : 0}
            </p>
          </div>
        </div>
      </div>

      {/* Role Breakdown */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Performance by Role</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(data.role_breakdown).map(([role, stats]) => (
              <div key={role} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">{role}</h3>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-600">
                    Count: <span className="font-medium text-gray-900">{stats.count}</span>
                  </p>
                  <p className="text-gray-600">
                    Total: <span className="font-medium text-gray-900">{Math.round(stats.total)}</span> / {stats.max}
                  </p>
                  <p className="text-gray-600">
                    Average: <span className="font-medium text-gray-900">
                      {stats.count > 0 ? Math.round(stats.total / stats.count) : 0}
                    </span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grade History */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Grade History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Session
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.grade_details.map((grade, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{grade.session_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {new Date(grade.session_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {grade.session_title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded">
                      {grade.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    {Math.round(grade.score)} / {grade.max_points}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {Math.round((grade.score / grade.max_points) * 100)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button
                      onClick={() => handleDownloadPDF(grade.session_id, grade.session_number, grade.role)}
                      className="inline-flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition"
                    >
                      <Download className="h-3 w-3" />
                      <span>PDF</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
