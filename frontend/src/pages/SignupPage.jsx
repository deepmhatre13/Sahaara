import React from 'react';
import { Link } from 'react-router-dom';
import SignupForm from '../components/auth/SignupForm';

export const SignupPage = () => {
  return (
    <div className="flex flex-col gap-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-[#1C2733]">Create Account</h2>
        <p className="text-sm text-[#8A97A5] mt-1">Join Sahaara for intelligent elder care</p>
      </div>

      <SignupForm />

      <p className="text-center text-sm text-[#8A97A5]">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-[#1E3A5F] hover:underline">
          Sign In
        </Link>
      </p>
    </div>
  );
};

export default SignupPage;
