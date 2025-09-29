'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { authAPI } from '@/lib/api';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();

  const navigation = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: '📊' },
    { name: 'Schools', href: '/admin/schools', icon: '🏫' },
    { name: 'Users', href: '/admin/users', icon: '👥' },
    { name: 'Teachers', href: '/admin/teachers', icon: '👨‍🏫' },
    { name: 'Classes', href: '/admin/classes', icon: '📚' },
    { name: 'Subjects', href: '/admin/subjects', icon: '📖' },
    { name: 'Rooms', href: '/admin/rooms', icon: '🚪' },
    { name: 'Timetables', href: '/admin/timetables', icon: '📅' },
    { name: 'Generate Timetable', href: '/admin/timetables/generate', icon: '🔄' },
  ];

  const isActive = (href: string) => pathname === href;

  const handleLogout = () => {
    authAPI.logout();
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'block' : 'hidden'} fixed inset-0 z-50 md:relative md:block md:inset-auto`}>
          <div className="flex flex-col w-64 h-full bg-white shadow-lg">
            <div className="flex items-center justify-between h-16 px-4 bg-blue-600">
              <h2 className="text-xl font-semibold text-white">Admin Panel</h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="md:hidden text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>

            <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  {item.name}
                </Link>
              ))}
            </nav>

            <div className="p-4 border-t">
              <button
                onClick={handleLogout}
                className="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Mobile Header */}
          <div className="md:hidden flex items-center justify-between h-16 px-4 bg-white shadow">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-600 hover:text-gray-900"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold">Admin Panel</h1>
          </div>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto p-4 md:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}