import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Send, Save } from 'lucide-react'
import toast, { Toaster } from 'react-hot-toast'
import api from '@/lib/api'

interface Assignment {
  id: number
  student_id: number
  student_name: string
  role: string | null
}

interface Student {
  id: number
  full_name: string
  email: string
  student_id: string
}

interface RubricSubsection {
  name: string
  description?: string
  max_points: number
  type: string
  min: number
  max: number
  step: number
}

interface RubricSection {
  name: string
  description?: string
  section?: boolean
  max_points: number
  subsections?: Record<string, RubricSubsection>
  // For backwards compatibility with non-sectioned criteria
  type?: string
  min?: number
  max?: number
  step?: number
}

interface Rubric {
  id: number
  role: string
  name: string
  max_points: number
  criteria: Record<string, RubricSection>
  deductions: Record<string, any>
}

export default function GradingWorkspace() {
  const { sessionId } = useParams()
  const [students, setStudents] = useState<Student[]>([])
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [selectedStudent, setSelectedStudent] = useState<Assignment | null>(null)
  const [showRoleModal, setShowRoleModal] = useState(false)
  const [selectedRole, setSelectedRole] = useState<string>('')
  const [rubric, setRubric] = useState<Rubric | null>(null)
  const [scores, setScores] = useState<Record<string, number>>({})
  const [feedbackNames, setFeedbackNames] = useState<Record<string, string>>({})
  const [deductions, setDeductions] = useState<Record<string, number>>({})
  const [comments, setComments] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [existingGradeId, setExistingGradeId] = useState<number | null>(null)
  const [useSlider, setUseSlider] = useState(false)
  const [courseId, setCourseId] = useState<number | null>(null)

  useEffect(() => {
    loadStudentsAndAssignments()
  }, [sessionId])

  useEffect(() => {
    if (selectedStudent && selectedStudent.role) {
      loadRubricAndGrade(selectedStudent.role, selectedStudent.student_id)
    }
  }, [selectedStudent])

  const loadStudentsAndAssignments = async () => {
    try {
      // Get session to extract course ID
      const sessionResponse = await api.get(`/api/sessions/${sessionId}`)
      setCourseId(sessionResponse.data.course_id)
      
      // Load all students in the course
      const studentsResponse = await api.get(`/api/students/course/${sessionResponse.data.course_id}`)
      setStudents(studentsResponse.data)
      
      // Load existing role assignments
      const assignmentsResponse = await api.get(`/api/sessions/${sessionId}/assignments`)
      const assignmentMap = new Map(
        assignmentsResponse.data.map((a: any) => [a.student_id, a.role])
      )
      
      // Create combined list with students and their roles (if assigned)
      const combinedList: Assignment[] = studentsResponse.data.map((student: Student) => ({
        id: student.id,
        student_id: student.id,
        student_name: student.full_name,
        role: assignmentMap.get(student.id) || null
      }))
      
      setAssignments(combinedList)
      
      if (combinedList.length > 0) {
        setSelectedStudent(combinedList[0])
      }
    } catch (error) {
      console.error('Failed to load students:', error)
      toast.error('Failed to load students')
    } finally {
      setLoading(false)
    }
  }

  const handleStudentSelect = (assignment: Assignment) => {
    // If student has no role, prompt for role selection
    if (!assignment.role) {
      setSelectedStudent(assignment)
      setShowRoleModal(true)
      setSelectedRole('')
    } else {
      setSelectedStudent(assignment)
    }
  }

  const handleRoleSelection = async () => {
    if (!selectedRole || !selectedStudent) return
    
    try {
      // Save role assignment
      await api.post(`/api/sessions/${sessionId}/assignments`, [{
        student_id: selectedStudent.student_id,
        role: selectedRole
      }])
      
      // Update the assignment with the new role
      const updatedAssignment = {
        ...selectedStudent,
        role: selectedRole
      }
      
      setAssignments(prevAssignments => 
        prevAssignments.map(a => 
          a.student_id === selectedStudent.student_id ? updatedAssignment : a
        )
      )
      
      setSelectedStudent(updatedAssignment)
      setShowRoleModal(false)
      toast.success('Role assigned successfully!', { icon: '🎯' })
      
      // Load rubric for the assigned role
      loadRubricAndGrade(selectedRole, selectedStudent.student_id)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to assign role')
    }
  }

  const loadRubricAndGrade = async (role: string, studentId: number) => {
    try {
      // Load rubric
      const rubricResponse = await api.get(`/api/rubrics/${role}`)
      setRubric(rubricResponse.data)
      
      // Initialize scores and feedback names
      const initialScores: Record<string, number> = {}
      const initialFeedbackNames: Record<string, string> = {}
      
      Object.entries(rubricResponse.data.criteria).forEach(([key, criterion]: [string, any]) => {
        if (criterion.subsections) {
          Object.entries(criterion.subsections).forEach(([subKey, subsection]: [string, any]) => {
            const fullKey = `${key}.${subKey}`
            initialScores[fullKey] = 0
            
            if (subsection.name?.includes('Feedback for') || subsection.name?.includes('Techn. Feedback')) {
              initialFeedbackNames[fullKey] = ''
            }
          })
        } else {
          initialScores[key] = 0
        }
      })
      
      // Try to load existing grade
      try {
        const gradeResponse = await api.get(`/api/grading/student/${studentId}/session/${sessionId}`)
        
        if (gradeResponse.data) {
          // Grade exists - populate fields
          setExistingGradeId(gradeResponse.data.id)
          setScores(gradeResponse.data.criterion_scores || initialScores)
          setDeductions(gradeResponse.data.deductions || {})
          setComments(gradeResponse.data.comments || '')
          setFeedbackNames(gradeResponse.data.feedback_names || initialFeedbackNames)
          toast.success('Loaded existing grade', { icon: '📝', duration: 2000 })
        } else {
          // No existing grade
          setExistingGradeId(null)
          setScores(initialScores)
          setFeedbackNames(initialFeedbackNames)
          setDeductions({})
          setComments('')
        }
      } catch (gradeError: any) {
        // No existing grade found (404) - that's okay
        if (gradeError.response?.status === 404) {
          setExistingGradeId(null)
          setScores(initialScores)
          setFeedbackNames(initialFeedbackNames)
          setDeductions({})
          setComments('')
        } else {
          throw gradeError
        }
      }
    } catch (error) {
      console.error('Failed to load rubric/grade:', error)
      toast.error('Failed to load grading data')
    }
  }

  const calculateTotal = () => {
    const rawScore = Object.values(scores).reduce((sum, score) => sum + score, 0)
    const deductionTotal = Object.values(deductions).reduce((sum, ded) => sum + ded, 0)
    return Math.max(0, rawScore - deductionTotal)
  }

  const handleSaveGrade = async (sendEmail = false) => {
    if (!selectedStudent || !rubric) return

    setSaving(true)
    try {
      const gradeData = {
        student_id: selectedStudent.student_id,
        session_id: Number(sessionId),
        rubric_template_id: rubric.id,
        criterion_scores: scores,
        deductions,
        comments,
        feedback_names: feedbackNames,
      }

      let response
      if (existingGradeId) {
        // Update existing grade
        response = await api.put(`/api/grading/${existingGradeId}`, gradeData)
        toast.success('Grade updated successfully!', {
          duration: 3000,
          icon: '✏️',
        })
      } else {
        // Create new grade
        response = await api.post('/api/grading/', gradeData)
        setExistingGradeId(response.data.id)
        toast.success('Grade saved successfully!', {
          duration: 3000,
          icon: '✅',
        })
      }

      if (sendEmail) {
        const gradeId = existingGradeId || response.data.id
        await api.post(`/api/grading/${gradeId}/send-email`)
        toast.success('Email sent to student!', {
          duration: 3000,
          icon: '📧',
        })
      }

      // Move to next student only if not sending email
      if (!sendEmail) {
        const currentIndex = assignments.findIndex(a => a.student_id === selectedStudent.student_id)
        if (currentIndex < assignments.length - 1) {
          setSelectedStudent(assignments[currentIndex + 1])
        }
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save grade', {
        duration: 4000,
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {courseId && (
        <Link to={`/courses/${courseId}`} className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Course
        </Link>
      )}

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Grading Workspace</h1>
        
        {/* Input Mode Toggle */}
        <div className="flex items-center space-x-3 bg-white rounded-lg shadow px-4 py-2">
          <span className="text-sm text-gray-600">Input Mode:</span>
          <button
            onClick={() => setUseSlider(false)}
            className={`px-3 py-1 rounded-md text-sm font-medium transition ${
              !useSlider 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Number Box
          </button>
          <button
            onClick={() => setUseSlider(true)}
            className={`px-3 py-1 rounded-md text-sm font-medium transition ${
              useSlider 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Slider
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Student List */}
        <div className="col-span-3">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold mb-3">Students</h2>
            <div className="space-y-2">
              {assignments.map((assignment) => (
                <button
                  key={assignment.id}
                  onClick={() => handleStudentSelect(assignment)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition ${
                    selectedStudent?.id === assignment.id
                      ? 'bg-primary-100 text-primary-700 font-medium'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="text-sm">{assignment.student_name}</div>
                  <div className="text-xs text-gray-500">
                    {assignment.role ? assignment.role : '⚠️ No role assigned'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Grading Form */}
        <div className="col-span-9">
          {selectedStudent && selectedStudent.role && rubric ? (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-6">
                <h2 className="text-xl font-semibold">{selectedStudent.student_name}</h2>
                <p className="text-gray-600">Role: {rubric.name}</p>
              </div>

              <div className="space-y-6">
                {/* Criteria */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">Criteria</h3>
                  <div className="space-y-6">
                    {Object.entries(rubric.criteria).map(([key, section]) => (
                      <div key={key} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                        {/* Section Header */}
                        <div className="mb-4">
                          <h4 className="font-semibold text-md text-gray-900">{section.name}</h4>
                          {section.description && (
                            <p className="text-xs text-gray-600 italic mt-1">{section.description}</p>
                          )}
                          <p className="text-xs text-gray-500 mt-1">
                            Subtotal: {section.max_points} pts
                          </p>
                        </div>

                        {/* Subsections or Direct Input */}
                        {section.subsections ? (
                          <div className="space-y-3 bg-white rounded-lg p-3">
                            {Object.entries(section.subsections).map(([subKey, subsection]) => {
                              const fullKey = `${key}.${subKey}`
                              const isFeedbackField = subsection.name?.includes('Feedback for') || subsection.name?.includes('Techn. Feedback')
                              
                              return (
                                <div key={subKey} className="py-2 border-b border-gray-100 last:border-0">
                                  <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 pr-4">
                                      <label className="block text-sm font-medium text-gray-800">
                                        {subsection.name}
                                      </label>
                                      {subsection.description && (
                                        <span className="text-xs text-gray-500 italic block mt-0.5">
                                          {subsection.description}
                                        </span>
                                      )}
                                      <span className="text-xs text-gray-500">Max: {subsection.max_points}</span>
                                    </div>
                                    
                                    <div className="flex items-center gap-3">
                                      {useSlider ? (
                                        <>
                                          <input
                                            type="range"
                                            min={subsection.min}
                                            max={subsection.max}
                                            step={subsection.step}
                                            value={scores[fullKey] || 0}
                                            onChange={(e) => setScores({ ...scores, [fullKey]: Number(e.target.value) })}
                                            className="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                                          />
                                          <span className="w-12 text-center font-semibold text-gray-700">
                                            {scores[fullKey] || 0}
                                          </span>
                                        </>
                                      ) : (
                                        <input
                                          type="number"
                                          min={subsection.min}
                                          max={subsection.max}
                                          step={subsection.step}
                                          value={scores[fullKey] || 0}
                                          onChange={(e) => setScores({ ...scores, [fullKey]: Number(e.target.value) })}
                                          className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center font-semibold"
                                        />
                                      )}
                                    </div>
                                  </div>
                                  
                                  {/* Add name input for feedback fields */}
                                  {isFeedbackField && (
                                    <div className="mt-2 ml-0">
                                      <input
                                        type="text"
                                        placeholder="Enter student name..."
                                        value={feedbackNames[fullKey] || ''}
                                        onChange={(e) => setFeedbackNames({ ...feedbackNames, [fullKey]: e.target.value })}
                                        className="w-full px-3 py-2 border border-blue-300 rounded-lg text-sm bg-blue-50 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                      />
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        ) : (
                          // Backwards compatibility for flat criteria
                          <div className="flex items-center justify-between">
                            <input
                              type="number"
                              min={section.min}
                              max={section.max}
                              step={section.step}
                              value={scores[key] || 0}
                              onChange={(e) => setScores({ ...scores, [key]: Number(e.target.value) })}
                              className="w-24 px-3 py-2 border border-gray-300 rounded-lg"
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Deductions */}
                {rubric.deductions && Object.keys(rubric.deductions).length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Deductions</h3>
                    <div className="space-y-3 bg-gray-50 rounded-lg p-4">
                      {Object.entries(rubric.deductions).map(([key, deduction]: [string, any]) => (
                        <label key={key} className="flex items-start space-x-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={deductions[key] > 0}
                            onChange={(e) => {
                              setDeductions({
                                ...deductions,
                                [key]: e.target.checked ? deduction.points : 0,
                              })
                            }}
                            className="mt-1 rounded border-gray-300"
                          />
                          <div className="flex-1">
                            <span className="text-sm font-medium text-gray-900 block">
                              {deduction.name}
                            </span>
                            {deduction.description && (
                              <span className="text-xs text-gray-600 italic">
                                {deduction.description}
                              </span>
                            )}
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* Comments */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Comments
                  </label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="Enter feedback for the student..."
                  />
                </div>

                {/* Score Summary */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center text-lg font-semibold">
                    <span>Total Score:</span>
                    <span className="text-primary-600">
                      {calculateTotal()} / {rubric.max_points}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-3">
                  <button
                    onClick={() => handleSaveGrade(false)}
                    disabled={saving}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
                  >
                    <Save className="h-4 w-4" />
                    <span>{saving ? 'Saving...' : 'Save Grade'}</span>
                  </button>
                  <button
                    onClick={() => handleSaveGrade(true)}
                    disabled={saving}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
                  >
                    <Send className="h-4 w-4" />
                    <span>{saving ? 'Saving...' : 'Save & Email'}</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-600">
                {selectedStudent && !selectedStudent.role 
                  ? 'Please assign a role to this student to begin grading.'
                  : 'Select a student to begin grading'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Role Selection Modal */}
      {showRoleModal && selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Assign Role to {selectedStudent.student_name}
            </h2>
            
            <p className="text-sm text-gray-600 mb-4">
              Select the role for this student before grading:
            </p>

            <div className="space-y-2 mb-6">
              {[
                { value: 'TT', label: 'Table Topic (TT)', points: '40 pts' },
                { value: 'TM', label: 'Toastmaster (TM)', points: '40 pts' },
                { value: 'Camera', label: 'Camera Assistant', points: '40 pts' },
                { value: 'SMT', label: 'Six Minute Talk (SMT)', points: '240 pts' },
                { value: 'Lead', label: 'Group Leader (Lead)', points: '200 pts' },
                { value: 'Reporter', label: 'Group Reporter', points: '200 pts' },
              ].map((role) => (
                <button
                  key={role.value}
                  onClick={() => setSelectedRole(role.value)}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 transition ${
                    selectedRole === role.value
                      ? 'border-primary-600 bg-primary-50 text-primary-900'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-semibold">{role.label}</div>
                      <div className="text-xs text-gray-500">{role.points}</div>
                    </div>
                    {selectedRole === role.value && (
                      <div className="text-primary-600">✓</div>
                    )}
                  </div>
                </button>
              ))}
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowRoleModal(false)
                  setSelectedRole('')
                  setSelectedStudent(null)
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleRoleSelection}
                disabled={!selectedRole}
                className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Assign Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
