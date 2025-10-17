/**
 * Protected route component that requires authentication.
 */
import { ReactNode, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAdmin?: boolean;
}

export function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { isAuthenticated, user, refreshUser } = useAuthStore();

  useEffect(() => {
    // Refresh user data on mount to ensure token is still valid
    refreshUser();
  }, [refreshUser]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check admin requirement
  if (requireAdmin && !user?.roles.includes('ADMIN')) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
