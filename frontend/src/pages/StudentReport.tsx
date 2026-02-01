import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download } from 'lucide-react'
import api from '@/lib/api'
import toast, { Toaster } from 'react-hot-toast'

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

interface StudentReportData {
  student_id: number
  student_name: string
  student_number: string
  sessions: SessionGrade[]
  role_totals: Record<string, number>
  role_counts: Record<string, number>
  total_score: number
  session_headers: SessionHeader[]
}

export default function StudentReport() {
  const { studentId } = useParams()
  const [reportData, setReportData] = useState<StudentReportData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReportData()
  }, [studentId])

  const loadReportData = async () => {
    try {
      const response = await api.get(`/api/reports/student/${studentId}/grade-sheet`)
      setReportData(response.data)
    } catch (error) {
      console.error('Failed to load report data:', error)
      toast.error('Failed to load report data')
    } finally {
      setLoading(false)
    }
  }

  const handleExportExcel = async () => {
    try {
      toast.loading('Generating Excel...')
      const response = await api.get(`/api/exports/student/${studentId}/grades.xlsx`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${reportData?.student_name}_Grades.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.dismiss()
      toast.success('Excel file downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to export Excel')
      console.error('Export failed:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!reportData) {
    return (
      <div>
        <Link to={`/students/${studentId}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Student
        </Link>
        <div className="text-center py-12">
          <p className="text-gray-600">No report data available yet.</p>
        </div>
      </div>
    )
  }

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
    const count = reportData.role_counts[role] || 0
    const maxPoints = roleMaxPoints[role] || 0
    totalPossibleScore += count * maxPoints
    totalObtainedScore += reportData.role_totals[role] || 0
  }

  return (
    <div>
      <Toaster position="top-right" />
      <Link to={`/students/${studentId}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Student
      </Link>

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Student Grade Report</h1>
        
        <button
          onClick={handleExportExcel}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          <Download className="h-4 w-4" />
          <span>Export Excel</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Student Header */}
        <div className="bg-gray-100 px-4 py-3 border-b border-gray-300">
          <h2 className="text-lg font-bold text-gray-900">
            STUDENT NAME: {reportData.student_name.toUpperCase()}
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
              {reportData.sessions.map((session, sessionIdx) => {
                const sessionHeader = reportData.session_headers[sessionIdx]
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
                  {(reportData.role_counts.TT || 0) * 40}
                </td>
                <td className="px-4 py-3 text-center text-sm text-red-700">
                  {(reportData.role_counts.TM || 0) * 40}
                </td>
                <td className="px-4 py-3 text-center text-sm text-red-700">
                  {(reportData.role_counts.Camera || 0) * 40}
                </td>
                <td className="px-4 py-3 text-center text-sm text-red-700">
                  {(reportData.role_counts.SMT || 0) * 480}
                </td>
                <td className="px-4 py-3 text-center text-sm text-red-700">
                  {(reportData.role_counts.Lead || 0) * 400}
                </td>
                <td className="px-4 py-3 text-center text-sm text-red-700">
                  {(reportData.role_counts.Reporter || 0) * 400}
                </td>
                <td className="px-4 py-3 text-center text-sm font-bold text-red-700">
                  {totalPossibleScore}
                </td>
              </tr>

              {/* Obtained Score Row */}
              <tr className="bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-700">Obtained Score</td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.TT || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.TM || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.Camera || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.SMT || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.Lead || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm text-gray-700">
                  {Math.round(reportData.role_totals.Reporter || 0)}
                </td>
                <td className="px-4 py-3 text-center text-sm font-bold text-gray-700">
                  {Math.round(totalObtainedScore)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
