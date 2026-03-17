'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Toast from './Toast';
import { authService } from '@/lib/auth';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const router = useRouter();

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): boolean => {
    return password.length >= 6;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateEmail(email)) {
      setError('E-mail inválido');
      return;
    }

    if (!validatePassword(password)) {
      setError('Senha deve ter no mínimo 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await authService.login(email, password, rememberMe);
      setToast({ message: 'Login realizado com sucesso!', type: 'success' });
      setTimeout(() => router.push('/dashboard'), 1500);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erro ao fazer login';
      setToast({ message: errorMessage, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="text-4xl">🎓</span>
          <h1 className="text-3xl font-bold">Portal RAG</h1>
        </div>
        <p className="text-text-secondary">Sistema de Questões e Chat Inteligente</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="w-full">
        {/* Email */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            <span>✉️</span> E-mail
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="seu@email.com"
            className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Password */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            <span>🔐</span> Senha
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-2.5 text-text-secondary hover:text-primary"
            >
              {showPassword ? '👁️‍🗨️' : '👁️'}
            </button>
          </div>
        </div>

        {/* Options */}
        <div className="flex items-center justify-between mb-6 text-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="w-4 h-4"
            />
            <span>Lembrar-me</span>
          </label>
          <Link href="#" className="text-primary hover:underline">
            Esqueci minha senha
          </Link>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-error rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-white py-2 rounded-lg font-semibold hover:bg-primary-hover disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
        >
          {loading ? <span className="animate-spin">⏳</span> : null}
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-text-secondary">ou</span>
        </div>
      </div>

      {/* Social Login */}
      <div className="space-y-2">
        <button
          type="button"
          className="w-full py-2 px-4 border border-border rounded-lg hover:bg-surface-2 transition-colors flex items-center justify-center gap-2"
        >
          <span>🔵</span> Entrar com Google
        </button>
        <button
          type="button"
          className="w-full py-2 px-4 border border-border rounded-lg hover:bg-surface-2 transition-colors flex items-center justify-center gap-2"
        >
          <span>🪟</span> Entrar com Microsoft
        </button>
      </div>

      {/* Signup Link */}
      <p className="text-center mt-6 text-text-secondary text-sm">
        Ainda não tem uma conta?{' '}
        <Link href="/register" className="text-primary font-semibold hover:underline">
          Cadastre-se
        </Link>
      </p>

      {/* Toast */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
