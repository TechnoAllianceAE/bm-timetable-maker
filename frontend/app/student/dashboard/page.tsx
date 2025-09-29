'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import TimetableViewer from '@/components/TimetableViewer';
import { timetableAPI } from '@/lib/api';
import Link from 'next/link';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [activeTimetable, setActiveTimetable] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await timetableAPI.list();
      const active = response.data.find((tt: any) => tt.isActive);
      setActiveTimetable(active);
    } catch (error) {
      console.error('Failed to fetch timetable:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['STUDENT', 'PARENT']}>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold">Student Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user?.name}!</span>
                <Link
                  href="/auth/login"
                  onClick={() => localStorage.clear()}
                  className="text-red-600 hover:text-red-800"
                >
                  Logout
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="text-gray-500">Loading your schedule...</div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Quick Info */}
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Your Information</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Name</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user?.name}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Role</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user?.role}</dd>
                  </div>
                </div>
              </div>

              {/* Timetable View */}
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Class Schedule</h2>
                {activeTimetable ? (
                  <TimetableViewer
                    timetableId={activeTimetable.id}
                    viewMode="class"
                  />
                ) : (
                  <p className="text-gray-500">No active timetable available.</p>
                )}
              </div>

              {/* Today's Classes */}
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Today's Classes</h2>
                <div className="space-y-3">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <div className="flex justify-between">
                      <div>
                        <h3 className="font-medium">Mathematics</h3>
                        <p className="text-sm text-gray-500">Room 101 • Mr. Johnson</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">9:00 AM - 9:45 AM</p>
                        <p className="text-xs text-gray-500">Period 1</p>
                      </div>
                    </div>
                  </div>
                  <div className="border-l-4 border-green-500 pl-4">
                    <div className="flex justify-between">
                      <div>
                        <h3 className="font-medium">Science</h3>
                        <p className="text-sm text-gray-500">Lab 1 • Ms. Smith</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">10:00 AM - 10:45 AM</p>
                        <p className="text-xs text-gray-500">Period 2</p>
                      </div>
                    </div>
                  </div>
                  <div className="border-l-4 border-purple-500 pl-4">
                    <div className="flex justify-between">
                      <div>
                        <h3 className="font-medium">English</h3>
                        <p className="text-sm text-gray-500">Room 203 • Mr. Brown</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">11:00 AM - 11:45 AM</p>
                        <p className="text-xs text-gray-500">Period 3</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}