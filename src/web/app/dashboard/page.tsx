'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import Sidebar from '@/components/Sidebar';
import DashboardContent from '@/components/DashboardContent';
import { authService } from '@/lib/auth';

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const userData = authService.getUser();
    if (userData) {
      setUser(userData);
    }
  }, []);

  const userInitials = user
    ? (user.username || user.email || 'U')
        .substring(0, 2)
        .toUpperCase()
    : 'U';

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          userName={user?.username || user?.name || 'Usuário'}
          userEmail={user?.email || 'email@example.com'}
          userInitials={userInitials}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col md:ml-72 ml-0">
          <DashboardContent />
        </div>
      </div>
    </ProtectedRoute>
  );
}
