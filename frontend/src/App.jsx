import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import ProtectedRoute from './routes/ProtectedRoute';

// Layouts
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import HealthPage from './pages/HealthPage';
import ActivityPage from './pages/ActivityPage';
import SOSPage from './pages/SOSPage';
import CaregiverPage from './pages/CaregiverPage';
import ChatbotPage from './pages/ChatbotPage';
import ReportsPage from './pages/ReportsPage';
import MedicationsPage from './pages/MedicationsPage';
import AppointmentsPage from './pages/AppointmentsPage';
import NotificationsPage from './pages/NotificationsPage';
import NotFoundPage from './pages/NotFoundPage';

export const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NotificationProvider>
          {/* Global Toast Provider */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#FFFFFF',
                color: '#1C2733',
                borderRadius: '12px',
                border: '1px solid #DDE3E8',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                padding: '12px 16px',
                fontSize: '14px',
              },
            }}
          />

          <Routes>
            {/* Unauthenticated Auth Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
            </Route>

            {/* Authenticated Dashboard Routes */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/health" element={<HealthPage />} />
              <Route path="/activity" element={<ActivityPage />} />
              <Route path="/sos" element={<SOSPage />} />
              <Route path="/caregiver" element={<CaregiverPage />} />
              <Route path="/chatbot" element={<ChatbotPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/medications" element={<MedicationsPage />} />
              <Route path="/appointments" element={<AppointmentsPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
            </Route>

            {/* Catch All 404 Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </NotificationProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;

