'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState } from 'react';

interface SidebarProps {
  userName: string;
  userEmail: string;
  userInitials: string;
}

export default function Sidebar({ userName, userEmail, userInitials }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/dashboard', label: 'Meus Chats', icon: '💬' },
    { href: '/dashboard', label: 'Upload de Dados', icon: '📤' },
    { href: '/dashboard', label: 'Configurações', icon: '⚙️' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    router.push('/login');
  };

  return (
    <>
      {/* Mobile Menu Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed left-4 top-4 z-50 bg-primary text-white p-2 rounded-lg"
      >
        ☰
      </button>

      {/* Sidebar */}
      <aside className={`fixed left-0 top-0 w-72 h-screen bg-white border-r border-border overflow-y-auto transition-transform duration-300 z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}>
        {/* Logo Section */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="text-2xl">📚</div>
            <h2 className="text-xl font-bold">Portal RAG</h2>
          </div>
          <p className="text-sm text-text-secondary">Sistema de Chat Inteligente</p>
        </div>

        {/* User Info */}
        <div className="p-4 bg-surface-2 m-3 rounded-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm">
              {userInitials}
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold">{userName}</h3>
              <p className="text-xs text-text-secondary">{userEmail}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                pathname === item.href
                  ? 'bg-surface-3 text-primary font-semibold'
                  : 'text-text-primary hover:bg-surface-2'
              }`}
              onClick={() => setIsOpen(false)}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Logout Button */}
        <div className="absolute bottom-4 left-4 right-4">
          <button
            onClick={handleLogout}
            className="w-full bg-error text-white py-2 rounded-lg hover:opacity-90 transition-opacity"
          >
            Sair
          </button>
        </div>
      </aside>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
