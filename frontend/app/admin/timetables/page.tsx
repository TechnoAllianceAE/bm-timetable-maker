'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

export default function AdminTimetablesPage() {
  const [timetables, setTimetables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAcademicYear, setSelectedAcademicYear] = useState('');

  useEffect(() => {
    fetchTimetables();
  }, []);

  const fetchTimetables = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:3000/timetables', {
        headers: { Authorization: `Bearer ${token}` },
        params: { academicYearId: selectedAcademicYear }
      });
      setTimetables(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch timetables');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (academicYearId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`http://localhost:3000/timetables/${academicYearId}/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Refresh list
      fetchTimetables();
      alert('Timetable generated successfully!');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate timetable');
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Timetables</h1>
        <Link href="/admin/users" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Manage Users
        </Link>
      </div>

      {error && <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">Error: {error}</div>}

      <div className="mb-6">
        <label className="mr-2">Academic Year:</label>
        <select value={selectedAcademicYear} onChange={(e) => setSelectedAcademicYear(e.target.value)} className="mr-4 p-2 border rounded">
          <option value="">All</option>
          <option value="2024-2025">2024-2025</option>
          <option value="2025-2026">2025-2026</option>
        </select>
        <button onClick={fetchTimetables} className="ml-4 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
          Filter
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Wellness Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {timetables.map((tt: any) => (
              <tr key={tt.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {tt.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    tt.status === 'DRAFT' ? 'bg-yellow-100 text-yellow-800' : tt.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {tt.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {tt.wellnessScore || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <Link href={`/timetable/${tt.id}`} className="text-indigo-600 hover:text-indigo-900 mr-4">
                    View
                  </Link>
                  <button onClick={() => handleGenerate(tt.academicYearId)} className="text-green-600 hover:text-green-900 mr-4">
                    Generate
                  </button>
                  <button className="text-blue-600 hover:text-blue-900">
                    Approve
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6">
        <button onClick={() => handleGenerate(selectedAcademicYear || 'current')} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
          Generate New Timetable
        </button>
      </div>
    </div>
  );
}