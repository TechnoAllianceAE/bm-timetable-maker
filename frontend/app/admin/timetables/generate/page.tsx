'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import AdminLayout from '@/components/AdminLayout';
import { timetableAPI, schoolAPI } from '@/lib/api';

interface School {
  id: string;
  name: string;
}

interface GenerationParams {
  schoolId: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  periodsPerDay: number;
  daysPerWeek: number;
  periodDuration: number;
  breakDuration: number;
  lunchDuration: number;
  constraints: {
    maxConsecutiveTeachingHours: number;
    minBreaksBetweenClasses: number;
    avoidBackToBackDifficultSubjects: boolean;
    preferMorningForDifficultSubjects: boolean;
    balanceTeacherWorkload: boolean;
  };
}

export default function GenerateTimetablePage() {
  const router = useRouter();
  const [schools, setSchools] = useState<School[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [params, setParams] = useState<GenerationParams>({
    schoolId: '',
    name: '',
    description: '',
    startDate: '',
    endDate: '',
    periodsPerDay: 8,
    daysPerWeek: 5,
    periodDuration: 45,
    breakDuration: 10,
    lunchDuration: 30,
    constraints: {
      maxConsecutiveTeachingHours: 3,
      minBreaksBetweenClasses: 1,
      avoidBackToBackDifficultSubjects: true,
      preferMorningForDifficultSubjects: true,
      balanceTeacherWorkload: true,
    },
  });

  useEffect(() => {
    fetchSchools();
  }, []);

  const fetchSchools = async () => {
    setLoading(true);
    try {
      const response = await schoolAPI.list();
      setSchools(response.data);
      if (response.data.length > 0) {
        setParams(prev => ({ ...prev, schoolId: response.data[0].id }));
      }
    } catch (error) {
      console.error('Failed to fetch schools:', error);
      setError('Failed to load schools');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setError('');
    setGenerationResult(null);

    try {
      const response = await timetableAPI.generate(params);
      setGenerationResult(response.data);

      if (response.data.status === 'success') {
        setTimeout(() => {
          router.push('/admin/timetables');
        }, 3000);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate timetable');
    } finally {
      setGenerating(false);
    }
  };

  const handleConstraintChange = (key: keyof typeof params.constraints, value: any) => {
    setParams(prev => ({
      ...prev,
      constraints: {
        ...prev.constraints,
        [key]: value,
      },
    }));
  };

  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Generate Timetable</h1>
          <p className="mt-1 text-sm text-gray-600">
            Configure parameters and constraints for automatic timetable generation
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading...</div>
          </div>
        ) : (
          <form onSubmit={handleGenerate} className="space-y-6 bg-white shadow rounded-lg p-6">
            {/* Basic Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    School
                  </label>
                  <select
                    required
                    value={params.schoolId}
                    onChange={(e) => setParams({ ...params, schoolId: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  >
                    <option value="">Select a school</option>
                    {schools.map((school) => (
                      <option key={school.id} value={school.id}>
                        {school.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Timetable Name
                  </label>
                  <input
                    type="text"
                    required
                    value={params.name}
                    onChange={(e) => setParams({ ...params, name: e.target.value })}
                    placeholder="e.g., Spring Semester 2024"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    value={params.description}
                    onChange={(e) => setParams({ ...params, description: e.target.value })}
                    rows={2}
                    placeholder="Optional description..."
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Start Date
                  </label>
                  <input
                    type="date"
                    required
                    value={params.startDate}
                    onChange={(e) => setParams({ ...params, startDate: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    End Date
                  </label>
                  <input
                    type="date"
                    required
                    value={params.endDate}
                    onChange={(e) => setParams({ ...params, endDate: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
              </div>
            </div>

            {/* Schedule Structure */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Schedule Structure</h2>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Periods Per Day
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="12"
                    required
                    value={params.periodsPerDay}
                    onChange={(e) =>
                      setParams({ ...params, periodsPerDay: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Days Per Week
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="7"
                    required
                    value={params.daysPerWeek}
                    onChange={(e) =>
                      setParams({ ...params, daysPerWeek: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Period Duration (min)
                  </label>
                  <input
                    type="number"
                    min="15"
                    max="90"
                    required
                    value={params.periodDuration}
                    onChange={(e) =>
                      setParams({ ...params, periodDuration: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Break Duration (min)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="30"
                    required
                    value={params.breakDuration}
                    onChange={(e) =>
                      setParams({ ...params, breakDuration: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
              </div>
            </div>

            {/* Constraints */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Constraints & Preferences</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Max Consecutive Teaching Hours
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="6"
                      value={params.constraints.maxConsecutiveTeachingHours}
                      onChange={(e) =>
                        handleConstraintChange(
                          'maxConsecutiveTeachingHours',
                          parseInt(e.target.value)
                        )
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Min Breaks Between Classes
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="3"
                      value={params.constraints.minBreaksBetweenClasses}
                      onChange={(e) =>
                        handleConstraintChange(
                          'minBreaksBetweenClasses',
                          parseInt(e.target.value)
                        )
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.avoidBackToBackDifficultSubjects}
                      onChange={(e) =>
                        handleConstraintChange(
                          'avoidBackToBackDifficultSubjects',
                          e.target.checked
                        )
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Avoid back-to-back difficult subjects
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.preferMorningForDifficultSubjects}
                      onChange={(e) =>
                        handleConstraintChange(
                          'preferMorningForDifficultSubjects',
                          e.target.checked
                        )
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Schedule difficult subjects in morning periods
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.balanceTeacherWorkload}
                      onChange={(e) =>
                        handleConstraintChange('balanceTeacherWorkload', e.target.checked)
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Balance teacher workload across days
                    </span>
                  </label>
                </div>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Generation Result */}
            {generationResult && (
              <div
                className={`rounded-md p-4 ${
                  generationResult.status === 'success'
                    ? 'bg-green-50'
                    : generationResult.status === 'partial'
                    ? 'bg-yellow-50'
                    : 'bg-red-50'
                }`}
              >
                <h3
                  className={`text-sm font-medium mb-2 ${
                    generationResult.status === 'success'
                      ? 'text-green-800'
                      : generationResult.status === 'partial'
                      ? 'text-yellow-800'
                      : 'text-red-800'
                  }`}
                >
                  {generationResult.status === 'success'
                    ? '✅ Timetable Generated Successfully!'
                    : generationResult.status === 'partial'
                    ? '⚠️ Partial Timetable Generated'
                    : '❌ Generation Failed'}
                </h3>
                {generationResult.message && (
                  <p
                    className={`text-sm ${
                      generationResult.status === 'success'
                        ? 'text-green-700'
                        : generationResult.status === 'partial'
                        ? 'text-yellow-700'
                        : 'text-red-700'
                    }`}
                  >
                    {generationResult.message}
                  </p>
                )}
                {generationResult.diagnostics && (
                  <div className="mt-3">
                    <h4 className="text-xs font-medium text-gray-700 mb-1">Diagnostics:</h4>
                    <pre className="text-xs text-gray-600 bg-white p-2 rounded overflow-x-auto">
                      {JSON.stringify(generationResult.diagnostics, null, 2)}
                    </pre>
                  </div>
                )}
                {generationResult.status === 'success' && (
                  <p className="text-sm text-green-600 mt-2">
                    Redirecting to timetables list...
                  </p>
                )}
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => router.push('/admin/timetables')}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={generating || !params.schoolId}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⚙️</span>
                    Generating...
                  </>
                ) : (
                  'Generate Timetable'
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </AdminLayout>
  );
}