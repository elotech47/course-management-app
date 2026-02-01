import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CourseDetail from './pages/CourseDetail'
import StudentDetail from './pages/StudentDetail'
import StudentReport from './pages/StudentReport'
import GradingWorkspace from './pages/GradingWorkspace'
import Reports from './pages/Reports'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />
      
      <Route element={<Layout />}>
        <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
        <Route path="/courses/:courseId" element={isAuthenticated ? <CourseDetail /> : <Navigate to="/login" />} />
        <Route path="/students/:studentId" element={isAuthenticated ? <StudentDetail /> : <Navigate to="/login" />} />
        <Route path="/students/:studentId/report" element={isAuthenticated ? <StudentReport /> : <Navigate to="/login" />} />
        <Route path="/grading/:sessionId" element={isAuthenticated ? <GradingWorkspace /> : <Navigate to="/login" />} />
        <Route path="/reports/:courseId" element={isAuthenticated ? <Reports /> : <Navigate to="/login" />} />
      </Route>
      
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

export default App
