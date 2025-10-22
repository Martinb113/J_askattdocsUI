/**
 * Main App component with routing.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Login } from '@/pages/Login';
import { Signup } from '@/pages/Signup';
import { Chat } from '@/pages/Chat';
import { Admin } from '@/pages/Admin';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Layout } from '@/components/Layout';

function App() {
  return (
    <>
      {/* Toast notifications */}
      <Toaster position="top-right" richColors closeButton expand={false} />

      <BrowserRouter>
        <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected routes */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Layout>
                <Chat />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <Layout>
                <Admin />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Redirect root to chat */}
        <Route path="/" element={<Navigate to="/chat" replace />} />

        {/* 404 */}
        <Route
          path="*"
          element={
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">404</h1>
                <p className="text-gray-600 mb-4">Page not found</p>
                <a href="/chat" className="text-primary-600 hover:text-primary-700 underline">
                  Go to Chat
                </a>
              </div>
            </div>
          }
        />
      </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
