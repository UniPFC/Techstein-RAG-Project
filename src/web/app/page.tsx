'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen bg-surface-1">
      <div className="text-center">
        <div className="animate-spin text-4xl mb-4">⏳</div>
        <p className="text-text-secondary">Redirecionando...</p>
      </div>
    </div>
  );
}
