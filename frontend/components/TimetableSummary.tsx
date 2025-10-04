'use client';

import { useEffect, useState } from 'react';
import { timetableAPI } from '@/lib/api';

interface SubjectSummary {
  subjectId: string;
  subjectName: string;
  actualPeriods: number;
  requiredPeriods: number | null;
  recommendedPeriods: number | null;
  status: 'below' | 'meets' | 'exceeds' | 'no-requirement';
  percentage: number;
}

interface TimetableSummaryData {
  totalPeriods: number;
  subjects: SubjectSummary[];
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

  const belowCount = summary.subjects.filter(s => s.status === 'below').length;
  const meetsCount = summary.subjects.filter(s => s.status === 'meets').length;
  const exceedsCount = summary.subjects.filter(s => s.status === 'exceeds').length;
  const noRequirementCount = summary.subjects.filter(s => s.status === 'no-requirement').length;

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
          <div className="text-sm font-medium text-blue-700">Exceeds Recommended</div>
          <div className="mt-2 text-3xl font-semibold text-blue-900">{exceedsCount}</div>
        </div>
      </div>

      {/* Subject Period Breakdown */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Subject Period Distribution</h3>

        <div className="space-y-4">
          {summary.subjects.map((subject) => (
            <div key={subject.subjectId} className="border-b border-gray-200 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium text-gray-900">{subject.subjectName}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadgeColor(subject.status)}`}>
                      {getStatusLabel(subject.status)}
                    </span>
                  </div>
                  <div className="mt-1 text-sm text-gray-600">
                    <span className="font-semibold">{subject.actualPeriods}</span> periods
                    {subject.requiredPeriods && (
                      <span className="ml-2">
                        / <span className="font-semibold">{subject.requiredPeriods}</span> required
                      </span>
                    )}
                    {subject.recommendedPeriods && (
                      <span className="ml-2 text-gray-500">
                        ({subject.recommendedPeriods} recommended)
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              {subject.requiredPeriods && (
                <div className="relative mt-3">
                  <div className="overflow-hidden h-6 text-xs flex rounded bg-gray-200">
                    <div
                      style={{ width: `${Math.min(subject.percentage, 100)}%` }}
                      className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${getStatusColor(subject.status)} transition-all duration-500`}
                    >
                      {subject.percentage > 10 && (
                        <span className="font-semibold">{subject.percentage}%</span>
                      )}
                    </div>
                  </div>
                  {subject.percentage > 100 && (
                    <div className="mt-1 text-xs text-blue-600">
                      {subject.percentage}% of requirement (exceeds by {subject.actualPeriods - subject.requiredPeriods} periods)
                    </div>
                  )}
                </div>
              )}

              {!subject.requiredPeriods && (
                <div className="mt-2 text-sm text-gray-500 italic">
                  No curriculum requirement set for this subject
                </div>
              )}
            </div>
          ))}
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
                  {belowCount} subject{belowCount > 1 ? 's do' : ' does'} not meet the minimum curriculum requirements.
                  Consider adjusting the timetable to ensure all subjects meet their required period counts.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {belowCount === 0 && summary.subjects.some(s => s.requiredPeriods) && (
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
                  All subjects with curriculum requirements meet or exceed their minimum period counts.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
