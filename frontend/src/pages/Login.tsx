/**
 * Login page component.
 */
import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();

  const [attid, setAttid] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login({ attid, password });
      navigate('/chat');
    } catch (error) {
      // Error is already set in store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            AI Chat Application
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <Input
              label="AT&T ID"
              type="text"
              value={attid}
              onChange={(e) => setAttid(e.target.value)}
              required
              placeholder="Enter your AT&T ID"
              autoComplete="username"
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </div>

          <div>
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign in
            </Button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/signup" className="font-medium text-primary-600 hover:text-primary-500">
                Sign up
              </Link>
            </p>
          </div>
        </form>

        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="text-xs text-center text-gray-500">
            <strong>Demo Admin Credentials:</strong>
            <br />
            AT&T ID: <code className="bg-gray-100 px-2 py-1 rounded">admin</code>
            <br />
            Password: <code className="bg-gray-100 px-2 py-1 rounded">Admin123!</code>
          </p>
        </div>
      </div>
    </div>
  );
}
