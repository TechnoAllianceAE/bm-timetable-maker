'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { schoolAPI, userAPI, teacherAPI, classAPI, timetableAPI } from '@/lib/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    schools: 0,
    users: 0,
    teachers: 0,
    classes: 0,
    timetables: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [schools, users, teachers, classes, timetables] = await Promise.all([
        schoolAPI.list(),
        userAPI.list(),
        teacherAPI.list(),
        classAPI.list(),
        timetableAPI.list(),
      ]);

      setStats({
        schools: schools.data.length,
        users: users.data.length,
        teachers: teachers.data.length,
        classes: classes.data.length,
        timetables: timetables.data.length,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { title: 'Schools', value: stats.schools, icon: '🏫', color: 'bg-blue-500' },
    { title: 'Users', value: stats.users, icon: '👥', color: 'bg-green-500' },
    { title: 'Teachers', value: stats.teachers, icon: '👨‍🏫', color: 'bg-purple-500' },
    { title: 'Classes', value: stats.classes, icon: '📚', color: 'bg-yellow-500' },
    { title: 'Timetables', value: stats.timetables, icon: '📅', color: 'bg-red-500' },
  ];

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Overview of your school management system
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading statistics...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {statCards.map((stat) => (
              <div
                key={stat.title}
                className="bg-white overflow-hidden shadow rounded-lg"
              >
                <div className="p-5">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 ${stat.color} rounded-md p-3 text-white text-2xl`}>
                      {stat.icon}
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          {stat.title}
                        </dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {stat.value}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <a
                href="/admin/timetables/generate"
                className="block w-full px-4 py-2 bg-blue-600 text-white text-center rounded-md hover:bg-blue-700"
              >
                Generate New Timetable
              </a>
              <a
                href="/admin/teachers"
                className="block w-full px-4 py-2 bg-green-600 text-white text-center rounded-md hover:bg-green-700"
              >
                Manage Teachers
              </a>
              <a
                href="/admin/classes"
                className="block w-full px-4 py-2 bg-purple-600 text-white text-center rounded-md hover:bg-purple-700"
              >
                Manage Classes
              </a>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">System Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Backend API</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Connected
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Timetable Engine</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Ready
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Database</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Operational
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}