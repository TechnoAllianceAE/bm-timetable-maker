'use client';

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            School Timetable Management SaaS
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Streamline scheduling, monitor teacher wellness, and optimize resources with our comprehensive platform for educational institutions.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Generate Timetables
            </h3>
            <p className="text-gray-600 mb-4">
              Automate schedule creation with AI-powered constraint satisfaction and wellness optimization.
            </p>
            <Link href="/admin/timetables" className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
              Get Started
            </Link>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.5l-1.39 1.39M21 12h-1M4 12H3m3.343-5.657l1.09-1.09m12.545 1.09l1.09-1.09M3 18.5V21M21 18.5V21M3 16.5v1.5M21 16.5v1.5M7 18.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zm12 0a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Wellness Monitoring
            </h3>
            <p className="text-gray-600 mb-4">
              Track teacher workload, detect burnout risks, and receive real-time alerts for better work-life balance.
            </p>
            <Link href="/teacher/dashboard" className="inline-block bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition">
              View Dashboard
            </Link>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110-5.714 4 4 0 010 5.714zM15 21.5a3.5 3.5 0 11-7 0 3.5 3.5 0 017 0zM3 7a6 6 0 0112 0v3h4a4 4 0 00-4 4v3H9V7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              User Management
            </h3>
            <p className="text-gray-600 mb-4">
              Manage users, roles, and permissions for administrators, teachers, students, and parents.
            </p>
            <Link href="/admin/users" className="inline-block bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition">
              Manage Users
            </Link>
          </div>
        </div>

        <div className="text-center mt-16">
          <p className="text-lg text-gray-600 mb-8">
            Ready to get started? Choose your role to access the platform.
          </p>
          <div className="space-x-4">
            <Link
              href="/auth/login"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition"
            >
              Login
            </Link>
            <Link
              href="/auth/register"
              className="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition"
            >
              Register
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}