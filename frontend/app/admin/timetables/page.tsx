'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AdminLayout from '@/components/AdminLayout';
import TimetableViewer from '@/components/TimetableViewer';
import { timetableAPI } from '@/lib/api';

interface Timetable {
  id: string;
  name: string;
  description?: string;
  schoolId: string;
  school?: { name: string };
  isActive: boolean;
  startDate: string;
  endDate: string;
  createdAt: string;
}

export default function TimetablesPage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimetable, setSelectedTimetable] = useState<Timetable | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'view'>('list');

  useEffect(() => {
    fetchTimetables();
  }, []);

  const fetchTimetables = async () => {
    try {
      const response = await timetableAPI.list();
      setTimetables(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch timetables:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await timetableAPI.activate(id);
      fetchTimetables();
    } catch (error) {
      console.error('Failed to activate timetable:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this timetable?')) {
      try {
        await timetableAPI.delete(id);
        fetchTimetables();
      } catch (error) {
        console.error('Failed to delete timetable:', error);
      }
    }
  };

  const handleView = (timetable: Timetable) => {
    setSelectedTimetable(timetable);
    setViewMode('view');
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              {viewMode === 'list' ? 'Timetables' : selectedTimetable?.name}
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              {viewMode === 'list'
                ? 'Manage and view generated timetables'
                : `Viewing timetable for ${selectedTimetable?.school?.name || 'School'}`}
            </p>
          </div>
          {viewMode === 'list' ? (
            <Link
              href="/admin/timetables/generate"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Generate New Timetable
            </Link>
          ) : (
            <button
              onClick={() => setViewMode('list')}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Back to List
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading timetables...</div>
          </div>
        ) : viewMode === 'list' ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            {timetables.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No timetables generated yet.</p>
                <Link
                  href="/admin/timetables/generate"
                  className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Generate Your First Timetable
                </Link>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {timetables.map((timetable) => (
                  <li key={timetable.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <div className="text-lg font-medium text-blue-600">
                              {timetable.name}
                            </div>
                            {timetable.isActive && (
                              <span className="ml-3 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                                Active
                              </span>
                            )}
                          </div>
                          {timetable.description && (
                            <p className="mt-1 text-sm text-gray-600">
                              {timetable.description}
                            </p>
                          )}
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex sm:space-x-6">
                              <p className="flex items-center text-sm text-gray-500">
                                🏫 {timetable.school?.name || 'N/A'}
                              </p>
                              <p className="flex items-center text-sm text-gray-500">
                                📅 {new Date(timetable.startDate).toLocaleDateString()} -{' '}
                                {new Date(timetable.endDate).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                              <p>
                                Created: {new Date(timetable.createdAt).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="ml-4 flex-shrink-0 flex space-x-2">
                          <button
                            onClick={() => handleView(timetable)}
                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                          >
                            View
                          </button>
                          {!timetable.isActive && (
                            <button
                              onClick={() => handleActivate(timetable.id)}
                              className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                            >
                              Activate
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(timetable.id)}
                            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : (
          selectedTimetable && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="mb-4">
                <h2 className="text-lg font-medium text-gray-900">Timetable View</h2>
                <p className="text-sm text-gray-600">
                  Complete weekly schedule for all classes
                </p>
              </div>
              <TimetableViewer timetableId={selectedTimetable.id} viewMode="class" />
            </div>
          )
        )}
      </div>
    </AdminLayout>
  );
}