/**
 * Main layout component with header and navigation.
 */
import { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { MessageSquare, LogOut } from 'lucide-react';
import { getInitials } from '@/lib/utils';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isAdmin = user?.roles.includes('ADMIN');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Navigation */}
            <div className="flex items-center space-x-8">
              <Link to="/chat" className="flex items-center space-x-2">
                <MessageSquare className="w-6 h-6 text-primary-600" />
                <span className="text-xl font-bold text-gray-900">AI Chat</span>
              </Link>

              <nav className="hidden md:flex space-x-4">
                <Link
                  to="/chat"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100"
                >
                  Chat
                </Link>
                {isAdmin && (
                  <Link
                    to="/admin"
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100"
                  >
                    Admin
                  </Link>
                )}
              </nav>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {user && (
                <>
                  {/* User Info */}
                  <div className="hidden sm:flex items-center space-x-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-600 text-white text-sm font-medium">
                      {getInitials(user.full_name)}
                    </div>
                    <div className="text-sm">
                      <p className="font-medium text-gray-900">{user.full_name}</p>
                      <p className="text-gray-500">{user.attid}</p>
                    </div>
                  </div>

                  {/* Logout Button */}
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
