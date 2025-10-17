/**
 * Signup page component.
 */
import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export function Signup() {
  const navigate = useNavigate();
  const { signup, isLoading, error, clearError } = useAuthStore();

  const [formData, setFormData] = useState({
    attid: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });

  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError('');

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setValidationError('Password must be at least 8 characters');
      return;
    }

    if (!/[A-Z]/.test(formData.password)) {
      setValidationError('Password must contain at least one uppercase letter');
      return;
    }

    if (!/[a-z]/.test(formData.password)) {
      setValidationError('Password must contain at least one lowercase letter');
      return;
    }

    if (!/[0-9]/.test(formData.password)) {
      setValidationError('Password must contain at least one digit');
      return;
    }

    try {
      await signup({
        attid: formData.attid,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
      navigate('/chat');
    } catch (error) {
      // Error is already set in store
    }
  };

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const displayError = validationError || error;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Get started with AI Chat
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {displayError && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {displayError}
            </div>
          )}

          <div className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              value={formData.full_name}
              onChange={(e) => updateField('full_name', e.target.value)}
              required
              placeholder="John Smith"
            />

            <Input
              label="AT&T ID"
              type="text"
              value={formData.attid}
              onChange={(e) => updateField('attid', e.target.value)}
              required
              placeholder="jsmith"
              autoComplete="username"
            />

            <Input
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => updateField('email', e.target.value)}
              required
              placeholder="jsmith@att.com"
              autoComplete="email"
            />

            <Input
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => updateField('password', e.target.value)}
              required
              placeholder="Min 8 chars, uppercase, lowercase, digit"
              autoComplete="new-password"
            />

            <Input
              label="Confirm Password"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => updateField('confirmPassword', e.target.value)}
              required
              placeholder="Confirm your password"
              autoComplete="new-password"
            />
          </div>

          <div>
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign up
            </Button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
