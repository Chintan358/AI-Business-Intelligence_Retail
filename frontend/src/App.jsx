import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardLayout from './layouts/DashboardLayout';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import BusinessProfilePage from './pages/BusinessProfilePage';
import DatasetUploadPage from './pages/DatasetUploadPage';
import DatasetHistoryPage from './pages/DatasetHistoryPage';
import DataPreviewPage from './pages/DataPreviewPage';
import AnalysisHubPage from './pages/AnalysisHubPage';
import AgentMonitorPage from './pages/AgentMonitorPage';
import ChatPage from './pages/ChatPage';
import ReportsPage from './pages/ReportsPage';
import ReportDetailsPage from './pages/ReportDetailsPage';
import ApprovalsPage from './pages/ApprovalsPage';
import RecommendationDetailsPage from './pages/RecommendationDetailsPage';
import AnalysisHistoryPage from './pages/AnalysisHistoryPage';
import UserManagementPage from './pages/UserManagementPage';
import AdminOverviewPage from './pages/AdminOverviewPage';
import SettingsPage from './pages/SettingsPage';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950 text-slate-400 text-xs">
        Authenticating enterprise session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Dashboard Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="profile" element={<BusinessProfilePage />} />
            <Route path="datasets/upload" element={<DatasetUploadPage />} />
            <Route path="datasets/history" element={<DatasetHistoryPage />} />
            <Route path="datasets/preview" element={<DataPreviewPage />} />
            <Route path="analysis" element={<AnalysisHubPage />} />
            <Route path="agents/monitor" element={<AgentMonitorPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="reports/:id" element={<ReportDetailsPage />} />
            <Route path="approvals" element={<ApprovalsPage />} />
            <Route path="recommendations/:id" element={<RecommendationDetailsPage />} />
            <Route path="history" element={<AnalysisHistoryPage />} />
            <Route path="admin" element={<ProtectedRoute adminOnly><AdminOverviewPage /></ProtectedRoute>} />
            <Route path="admin/users" element={<ProtectedRoute adminOnly><UserManagementPage /></ProtectedRoute>} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
