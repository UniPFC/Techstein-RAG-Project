'use client';

import { useState, useEffect } from 'react';
import { authService } from '@/lib/auth';
import api from '@/lib/api';

export default function DashboardContent() {
  const [stats, setStats] = useState({
    totalChats: 0,
    totalMessages: 0,
    totalChatTypes: 0,
    totalChunks: 0,
  });
  const [chats, setChats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load mock data for demo
      const mockChats = [
        {
          id: 1,
          title: 'Estudo ENEM 2024',
          chat_type_id: 1,
          created_at: '2024-03-15T10:30:00Z',
          message_count: 15,
        },
        {
          id: 2,
          title: 'Matemática Básica',
          chat_type_id: 2,
          created_at: '2024-03-14T09:15:00Z',
          message_count: 8,
        },
        {
          id: 3,
          title: 'História do Brasil',
          chat_type_id: 3,
          created_at: '2024-03-13T13:00:00Z',
          message_count: 12,
        },
      ];

      setChats(mockChats);
      setStats({
        totalChats: mockChats.length,
        totalMessages: 35,
        totalChatTypes: 3,
        totalChunks: 350,
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return <div className="p-8 text-center">Carregando...</div>;
  }

  return (
    <div className="flex-1">
      {/* Header */}
      <div className="bg-white border-b border-border p-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-hover">
          ➕ Novo Chat
        </button>
      </div>

      {/* Main Content */}
      <div className="p-6 overflow-auto">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon="💬" label="Chats Totais" value={stats.totalChats} />
          <StatCard icon="📢" label="Mensagens" value={stats.totalMessages} />
          <StatCard icon="📂" label="Tipos de Chat" value={stats.totalChatTypes} />
          <StatCard icon="📄" label="Chunks" value={stats.totalChunks} />
        </div>

        {/* Recent Chats */}
        <div className="bg-white rounded-lg border border-border overflow-hidden">
          <div className="p-6 border-b border-border">
            <h2 className="text-lg font-semibold">Chats Recentes</h2>
          </div>
          <div className="divide-y divide-border">
            {chats.length === 0 ? (
              <div className="p-6 text-center text-text-secondary">
                Nenhum chat criado ainda
              </div>
            ) : (
              chats.map((chat) => (
                <div key={chat.id} className="p-4 hover:bg-surface-2 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-text-primary">{chat.title}</h3>
                      <p className="text-sm text-text-secondary">
                        {chat.message_count} mensagens • {formatDate(chat.created_at)}
                      </p>
                    </div>
                    <button className="text-primary hover:text-primary-hover">→</button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: number }) {
  return (
    <div className="bg-white p-4 rounded-lg border border-border">
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <p className="text-text-secondary text-sm">{label}</p>
      </div>
      <p className="text-3xl font-bold text-primary">{value}</p>
    </div>
  );
}
