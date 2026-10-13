import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';

export const LoginPage = () => {
  return (
    <div className="flex flex-col gap-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#1C2733]">Sign In</h2>
        <p className="text-sm text-[#8A97A5] mt-1">Access your personalized care dashboard</p>
      </div>

      <LoginForm />

      <p className="text-center text-sm text-[#8A97A5]">
        Don't have an account yet?{' '}
        <Link to="/signup" className="font-semibold text-[#1E3A5F] hover:underline">
          Create Account
        </Link>
      </p>
    </div>
  );
};

export default LoginPage;
