'use client';

import LoginForm from '@/components/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 relative overflow-hidden">
      {/* Floating shapes background */}
      <div className="absolute top-10 left-10 w-20 h-20 bg-blue-200 rounded-full opacity-20 blur-2xl"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-indigo-200 rounded-full opacity-20 blur-2xl"></div>
      <div className="absolute top-1/2 left-1/3 w-16 h-16 bg-purple-200 rounded-full opacity-20 blur-2xl"></div>

      {/* Content */}
      <LoginForm />
    </div>
  );
}
