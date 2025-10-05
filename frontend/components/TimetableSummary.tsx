'use client';

import { useEffect, useState } from 'react';
import { timetableAPI } from '@/lib/api';

interface SubjectSummary {
  subjectId: string;
  subjectName: string;
  actualPeriods: number;
  requiredPeriods: number | null;
  status: 'below' | 'meets' | 'exceeds' | 'no-requirement';
  percentage: number;
}

interface ClassSummary {
  classId: string;
  className: string;
  grade: number;
  subjects: SubjectSummary[];
  totalActual: number;
  totalRequired: number;
}

interface TimetableSummaryData {
  totalPeriods: number;
  classes: ClassSummary[];
}

interface TimetableSummaryProps {
  timetableId: string;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'below':
      return 'bg-red-500';
    case 'meets':
      return 'bg-green-500';
    case 'exceeds':
      return 'bg-blue-500';
    case 'no-requirement':
      return 'bg-gray-400';
    default:
      return 'bg-gray-400';
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'below':
      return 'Below Requirement';
    case 'meets':
      return 'Meets Requirement';
    case 'exceeds':
      return 'Exceeds Recommended';
    case 'no-requirement':
      return 'No Requirement Set';
    default:
      return 'Unknown';
  }
};

const getStatusBadgeColor = (status: string) => {
  switch (status) {
    case 'below':
      return 'bg-red-100 text-red-800';
    case 'meets':
      return 'bg-green-100 text-green-800';
    case 'exceeds':
      return 'bg-blue-100 text-blue-800';
    case 'no-requirement':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function TimetableSummary({ timetableId }: TimetableSummaryProps) {
  const [summary, setSummary] = useState<TimetableSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSummary();
  }, [timetableId]);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await timetableAPI.getSummary(timetableId);
      setSummary(response.data.data);
    } catch (err) {
      console.error('Failed to fetch timetable summary:', err);
      setError('Failed to load timetable summary');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading summary...</div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-700">
        {error || 'No summary data available'}
      </div>
    );
  }

  // Handle case where classes might not exist (backward compatibility)
  if (!summary.classes || summary.classes.length === 0) {
    return (
      <div className="rounded-md border border-gray-200 bg-gray-50 p-4 text-gray-700">
        No class data available. This timetable may have been generated before classwise analytics were implemented.
      </div>
    );
  }

  // Calculate overall stats from all classes
  const allSubjects = summary.classes.flatMap(c => c.subjects);
  const belowCount = allSubjects.filter(s => s.status === 'below').length;
  const meetsCount = allSubjects.filter(s => s.status === 'meets').length;
  const exceedsCount = allSubjects.filter(s => s.status === 'exceeds').length;

  // Get all unique subjects across all classes
  const uniqueSubjects = new Set(allSubjects.map(s => s.subjectName));

  return (
    <div className="space-y-6">
      {/* Overview Statistics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm font-medium text-gray-500">Total Periods</div>
          <div className="mt-2 text-3xl font-semibold text-gray-900">{summary.totalPeriods}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-4">
          <div className="text-sm font-medium text-green-700">Meets Requirements</div>
          <div className="mt-2 text-3xl font-semibold text-green-900">{meetsCount}</div>
        </div>
        <div className="bg-red-50 rounded-lg border border-red-200 p-4">
          <div className="text-sm font-medium text-red-700">Below Requirements</div>
          <div className="mt-2 text-3xl font-semibold text-red-900">{belowCount}</div>
        </div>
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
          <div className="text-sm font-medium text-blue-700">Exceeds Required</div>
          <div className="mt-2 text-3xl font-semibold text-blue-900">{exceedsCount}</div>
        </div>
      </div>

      {/* Classwise Subject Period Distribution Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Subject Period Distribution by Class</h3>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50">
                  Class
                </th>
                {Array.from(uniqueSubjects).sort().map(subjectName => (
                  <th key={subjectName} className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {subjectName}
                  </th>
                ))}
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-100">
                  Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {summary.classes.map((classData) => (
                <tr key={classData.classId} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                    {classData.className}
                  </td>
                  {Array.from(uniqueSubjects).sort().map(subjectName => {
                    const subject = classData.subjects.find(s => s.subjectName === subjectName);
                    if (!subject) {
                      return <td key={subjectName} className="px-4 py-3 text-center text-sm text-gray-400">-</td>;
                    }

                    const cellColor = subject.status === 'below' ? 'text-red-600 font-semibold'
                      : subject.status === 'meets' ? 'text-green-600 font-semibold'
                      : subject.status === 'exceeds' ? 'text-blue-600 font-semibold'
                      : 'text-gray-600';

                    return (
                      <td key={subjectName} className={`px-4 py-3 text-center text-sm ${cellColor}`}>
                        {subject.actualPeriods}
                        {subject.requiredPeriods && (
                          <span className="text-xs text-gray-500">/{subject.requiredPeriods}</span>
                        )}
                      </td>
                    );
                  })}
                  <td className="px-4 py-3 text-center text-sm font-semibold bg-gray-50">
                    {classData.totalActual}
                    {classData.totalRequired > 0 && (
                      <span className="text-xs text-gray-500">/{classData.totalRequired}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 text-xs text-gray-500">
          <p><span className="text-red-600 font-semibold">Red</span> = Below requirement | <span className="text-green-600 font-semibold">Green</span> = Meets requirement | <span className="text-blue-600 font-semibold">Blue</span> = Exceeds requirement</p>
        </div>
      </div>

      {/* Curriculum Compliance Summary */}
      {belowCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Curriculum Compliance Warning</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  {belowCount} subject assignment{belowCount > 1 ? 's do' : ' does'} not meet the minimum curriculum requirements across all classes.
                  Consider adjusting the timetable to ensure all subjects meet their required period counts.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {belowCount === 0 && allSubjects.some(s => s.requiredPeriods) && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Curriculum Compliant</h3>
              <div className="mt-2 text-sm text-green-700">
                <p>
                  All subject assignments across all classes meet or exceed their minimum period requirements.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
