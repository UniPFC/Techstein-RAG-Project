'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Toast from '@/components/Toast';
import { authService } from '@/lib/auth';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError('Preencha todos os campos');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem');
      return;
    }

    if (formData.password.length < 6) {
      setError('Senha deve ter no mínimo 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await authService.register(formData.email, formData.password, formData.username);
      setToast({ message: 'Cadastro realizado com sucesso!', type: 'success' });
      setTimeout(() => router.push('/dashboard'), 1500);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erro ao fazer cadastro';
      setToast({ message: errorMessage, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 relative overflow-hidden p-4">
      {/* Background shapes */}
      <div className="absolute top-10 left-10 w-20 h-20 bg-blue-200 rounded-full opacity-20 blur-2xl"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-indigo-200 rounded-full opacity-20 blur-2xl"></div>

      {/* Content */}
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="text-4xl">🎓</span>
            <h1 className="text-3xl font-bold">Portal RAG</h1>
          </div>
          <p className="text-text-secondary">Crie sua conta</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="w-full bg-white p-6 rounded-lg shadow-lg border border-border">
          {/* Username */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              <span>👤</span> Nome de usuário
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="seu_usuario"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Email */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              <span>✉️</span> E-mail
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="seu@email.com"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Password */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              <span>🔐</span> Senha
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Mínimo 6 caracteres"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Confirm Password */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">
              <span>🔐</span> Confirmar Senha
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Digite a senha novamente"
              className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
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
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        {/* Login Link */}
        <p className="text-center mt-6 text-text-secondary text-sm">
          Já tem uma conta?{' '}
          <Link href="/login" className="text-primary font-semibold hover:underline">
            Faça login
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
    </div>
  );
}
