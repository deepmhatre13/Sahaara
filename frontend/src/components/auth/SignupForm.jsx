import React, { useState } from 'react';
import { User, Mail, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Input from '../common/Input';
import Button from '../common/Button';
import GoogleSignInButton from './GoogleSignInButton';
import useAuth from '../../hooks/useAuth';
import { isValidEmail, isValidPassword } from '../../utils/validators';
import { getApiErrorMessage } from '../../utils/apiError';

export const SignupForm = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    const newErrors = {};
    if (!fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }
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
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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
      await signup(fullName.trim(), email.trim(), password);
      toast.success('Account created successfully! Welcome to Sahaara.');
      navigate('/dashboard');
    } catch (err) {
      toast.error(getApiErrorMessage(err, 'Failed to create account. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Full Name"
        type="text"
        placeholder="Grandpa John"
        icon={User}
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        error={errors.fullName}
        disabled={isLoading}
      />

      <Input
        label="Email Address"
        type="email"
        placeholder="john@example.com"
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

      <Input
        label="Confirm Password"
        type="password"
        placeholder="••••••••"
        icon={Lock}
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        error={errors.confirmPassword}
        disabled={isLoading}
      />

      <Button type="submit" variant="primary" size="lg" fullWidth isLoading={isLoading} className="mt-2">
        Create Account
      </Button>

      <div className="relative my-2 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#DDE3E8]"></div>
        </div>
        <span className="relative bg-white px-3 text-xs text-[#8A97A5] uppercase font-semibold">
          Or continue with
        </span>
      </div>

      <GoogleSignInButton text="Sign up with Google" />
    </form>
  );
};

export default SignupForm;

