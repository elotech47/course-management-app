import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download, Mail } from 'lucide-react'
import api from '@/lib/api'

interface SessionHeader {
  id: number
  date: string
  session_number: number
  title: string
}

interface SessionGrade {
  session_id: number
  role: string | null
  score: number | null
}

interface StudentRow {
  student_id: number
  student_name: string
  student_number: string
  sessions: SessionGrade[]
  role_totals: Record<string, number>
  role_counts: Record<string, number>
  total_score: number
}

interface GradeSheetData {
  session_headers: SessionHeader[]
  students: StudentRow[]
}

export default function Reports() {
  const { courseId } = useParams()
  const [gradeSheet, setGradeSheet] = useState<GradeSheetData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGradeSheet()
  }, [courseId])

  const loadGradeSheet = async () => {
    try {
      const response = await api.get(`/api/reports/course/${courseId}/grade-sheet`)
      setGradeSheet(response.data)
    } catch (error) {
      console.error('Failed to load grade sheet:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const response = await api.get(`/api/exports/course/${courseId}/grades.${format}`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `grades.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!gradeSheet || gradeSheet.students.length === 0) {
    return (
      <div>
        <Link to={`/courses/${courseId}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Course
        </Link>
        <div className="text-center py-12">
          <p className="text-gray-600">No grade data available yet.</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Link to={`/courses/${courseId}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Course
      </Link>

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Final Grade Report</h1>
        
        <div className="flex space-x-2">
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExport('xlsx')}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            <Download className="h-4 w-4" />
            <span>Export Excel</span>
          </button>
        </div>
      </div>

      <div className="space-y-8">
        {gradeSheet.students.map((student, studentIdx) => {
          // Define max points per role
          const roleMaxPoints: Record<string, number> = {
            'TT': 40,
            'TM': 40,
            'Camera': 40,
            'SMT': 480,
            'Lead': 400,
            'Reporter': 400
          }
          
          // Calculate total possible score and total obtained score
          let totalPossibleScore = 0
          let totalObtainedScore = 0
          
          for (const role of ['TT', 'TM', 'Camera', 'SMT', 'Lead', 'Reporter']) {
            const count = student.role_counts[role] || 0
            const maxPoints = roleMaxPoints[role] || 0
            totalPossibleScore += count * maxPoints
            totalObtainedScore += student.role_totals[role] || 0
          }
          
          return (
          <div key={student.student_id} className="bg-white rounded-lg shadow overflow-hidden">
            {/* Student Header */}
            <div className="bg-gray-100 px-4 py-3 border-b border-gray-300">
              <h2 className="text-lg font-bold text-gray-900">
                STUDENT NAME: {student.student_name.toUpperCase()}
              </h2>
            </div>

            {/* Grade Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      DATES
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      TT
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      TM
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CAMERA
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SMT
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      LEAD
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      REPORTER
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {/* Session rows */}
                  {student.sessions.map((session, sessionIdx) => {
                    const sessionHeader = gradeSheet.session_headers[sessionIdx]
                    const sessionScore = session.score !== null ? Math.round(session.score) : null
                    
                    return (
                      <tr key={sessionIdx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {sessionHeader?.date || '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'TT' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'TM' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'Camera' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'SMT' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'Lead' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {session.role === 'Reporter' && sessionScore !== null ? sessionScore : '-'}
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900">
                          {sessionScore !== null ? sessionScore : '-'}
                        </td>
                      </tr>
                    )
                  })}

                  {/* Total Score Row */}
                  <tr className="bg-red-50 font-semibold border-t-2 border-red-300">
                    <td className="px-4 py-3 text-sm text-red-700">Total Score</td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.TT || 0) * 40}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.TM || 0) * 40}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.Camera || 0) * 40}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.SMT || 0) * 480}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.Lead || 0) * 400}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-red-700">
                      {(student.role_counts.Reporter || 0) * 400}
                    </td>
                    <td className="px-4 py-3 text-center text-sm font-bold text-red-700">
                      {totalPossibleScore}
                    </td>
                  </tr>

                  {/* Obtained Score Row */}
                  <tr className="bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-700">Obtained Score</td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.TT || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.TM || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.Camera || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.SMT || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.Lead || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">
                      {Math.round(student.role_totals.Reporter || 0)}
                    </td>
                    <td className="px-4 py-3 text-center text-sm font-bold text-gray-700">
                      {Math.round(totalObtainedScore)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          )
        })}
      </div>
    </div>
  )
}
