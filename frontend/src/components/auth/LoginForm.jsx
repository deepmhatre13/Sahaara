import React, { useState } from 'react';
import { Mail, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Input from '../common/Input';
import Button from '../common/Button';
import GoogleSignInButton from './GoogleSignInButton';
import useAuth from '../../hooks/useAuth';
import { isValidEmail, isValidPassword } from '../../utils/validators';
import { getApiErrorMessage } from '../../utils/apiError';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    const newErrors = {};
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (!isValidPassword(password)) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading) return; // duplicate-submit protection
    if (!validate()) return;

    setIsLoading(true);
    setErrors({});
    try {
      await login(email.trim(), password);
      toast.success('Welcome back to Sahaara!');
      navigate('/dashboard');
    } catch (err) {
      const msg = getApiErrorMessage(err, 'Invalid email or password.');
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Email Address"
        type="email"
        placeholder="elder@example.com"
        icon={Mail}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        disabled={isLoading}
      />

      <Input
        label="Password"
        type="password"
        placeholder="••••••••"
        icon={Lock}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        disabled={isLoading}
      />

      <Button type="submit" variant="primary" size="lg" fullWidth isLoading={isLoading} className="mt-2">
        Sign In
      </Button>

      <div className="relative my-2 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#DDE3E8]"></div>
        </div>
        <span className="relative bg-white px-3 text-xs text-[#8A97A5] uppercase font-semibold">
          Or continue with
        </span>
      </div>

      <GoogleSignInButton text="Sign in with Google" />
    </form>
  );
};

export default LoginForm;

