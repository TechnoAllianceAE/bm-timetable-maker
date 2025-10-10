'use client';

import { useState, useEffect } from 'react';
import { timetableAPI } from '@/lib/api';

interface TimetableEntry {
  id: string;
  class_id: string;
  class_name: string;
  subject_id: string;
  subject_name: string;
  teacher_id: string;
  teacher_name: string;
  room_id: string;
  room_name: string;
  time_slot_id: string;
  day_of_week: string;
  period_number: number;
  start_time: string;
  end_time: string;
}

interface TimetableView {
  id: string;
  name: string;
  status: string;
  evaluation_score: number;
  generation_time: number;
  created_at: string;
  entries: TimetableEntry[];
  metadata: {
    engine_version: string;
    total_entries: number;
    conflicts: number;
    suggestions_count: number;
  };
}

interface Props {
  timetableId: string;
  sessionData?: any;
}

export default function TimetableResultsView({ timetableId, sessionData }: Props) {
  const [timetable, setTimetable] = useState<TimetableView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'grid' | 'list'>('grid');
  const [selectedClass, setSelectedClass] = useState<string>('all');

  useEffect(() => {
    fetchTimetable();
  }, [timetableId]);

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      const response = await timetableAPI.getTimetableView(timetableId);
      setTimetable(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load timetable');
    } finally {
      setLoading(false);
    }
  };

  const getUniqueClasses = () => {
    if (!timetable) return [];
    const classes = Array.from(new Set(timetable.entries.map(e => e.class_name)));
    return classes.sort();
  };

  const getFilteredEntries = () => {
    if (!timetable) return [];
    if (selectedClass === 'all') return timetable.entries;
    return timetable.entries.filter(e => e.class_name === selectedClass);
  };

  const getWeeklySchedule = () => {
    const entries = getFilteredEntries();
    const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
    const maxPeriods = Math.max(...entries.map(e => e.period_number), 7);
    
    const schedule: { [key: string]: { [key: number]: TimetableEntry[] } } = {};
    
    days.forEach(day => {
      schedule[day] = {};
      for (let period = 1; period <= maxPeriods; period++) {
        schedule[day][period] = entries.filter(
          e => e.day_of_week === day && e.period_number === period
        );
      }
    });
    
    return { schedule, days, maxPeriods };
  };

  const getScoreColor = (score: number) => {
    if (score >= 900) return 'text-green-600';
    if (score >= 800) return 'text-yellow-600';
    if (score >= 700) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreGrade = (score: number) => {
    if (score >= 900) return 'A';
    if (score >= 800) return 'B';
    if (score >= 700) return 'C';
    if (score >= 600) return 'D';
    return 'F';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading timetable...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">{error}</div>
        <button
          onClick={fetchTimetable}
          className="mt-2 text-sm text-red-600 hover:text-red-800"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!timetable) return null;

  const { schedule, days, maxPeriods } = getWeeklySchedule();
  const uniqueClasses = getUniqueClasses();

  return (
    <div className="space-y-6">
      {/* Header with Quality Metrics */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{timetable.name}</h1>
            <p className="text-sm text-gray-500">
              Generated {new Date(timetable.created_at).toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getScoreColor(timetable.evaluation_score)}`}>
              {timetable.evaluation_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-500">Quality Score</div>
          </div>
        </div>

        {/* Quality Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className={`text-2xl font-bold ${getScoreColor(timetable.evaluation_score)}`}>
              {getScoreGrade(timetable.evaluation_score)}
            </div>
            <div className="text-xs text-gray-600">Grade</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {timetable.generation_time.toFixed(1)}s
            </div>
            <div className="text-xs text-gray-600">Generation Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {timetable.metadata.total_entries}
            </div>
            <div className="text-xs text-gray-600">Total Entries</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${
              timetable.metadata.conflicts === 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {timetable.metadata.conflicts}
            </div>
            <div className="text-xs text-gray-600">Conflicts</div>
          </div>
        </div>

        {/* Engine Information */}
        <div className="mt-4 text-xs text-gray-500">
          Engine: {timetable.metadata.engine_version} • Status: {timetable.status}
        </div>
      </div>

      {/* View Controls */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                View Class
              </label>
              <select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                className="border border-gray-300 rounded px-3 py-1 text-sm"
              >
                <option value="all">All Classes</option>
                {uniqueClasses.map(className => (
                  <option key={className} value={className}>
                    {className}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              onClick={() => setSelectedView('grid')}
              className={`px-3 py-1 text-sm ${
                selectedView === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              📅 Grid View
            </button>
            <button
              onClick={() => setSelectedView('list')}
              className={`px-3 py-1 text-sm ${
                selectedView === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              📋 List View
            </button>
          </div>
        </div>
      </div>

      {/* Timetable Display */}
      {selectedView === 'grid' ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period / Day
                  </th>
                  {days.map(day => (
                    <th key={day} className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {day.substring(0, 3)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Array.from({ length: maxPeriods }, (_, i) => i + 1).map(period => (
                  <tr key={period}>
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Period {period}
                    </td>
                    {days.map(day => (
                      <td key={`${day}-${period}`} className="px-2 py-2">
                        <div className="space-y-1">
                          {schedule[day][period]?.map(entry => (
                            <div
                              key={entry.id}
                              className="bg-blue-50 border border-blue-200 rounded p-2 text-xs"
                            >
                              <div className="font-semibold text-blue-900">
                                {entry.subject_name}
                              </div>
                              <div className="text-blue-700">
                                {entry.class_name}
                              </div>
                              <div className="text-blue-600">
                                {entry.teacher_name}
                              </div>
                              <div className="text-blue-500">
                                {entry.room_name}
                              </div>
                            </div>
                          ))}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Schedule Entries ({getFilteredEntries().length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {getFilteredEntries().map(entry => (
              <div key={entry.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {entry.subject_name} - {entry.class_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {entry.teacher_name} • {entry.room_name}
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <div>{entry.day_of_week.substring(0, 3)} P{entry.period_number}</div>
                    <div>{entry.start_time} - {entry.end_time}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Information */}
      {sessionData?.rankings && sessionData.rankings.length > 1 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Alternative Solutions
          </h3>
          <div className="space-y-2">
            {sessionData.rankings.map(([id, score]: [string, number], index: number) => (
              <div key={id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm text-gray-700">
                  Solution {index + 1} {index === 0 && '(Current)'}
                </span>
                <span className={`text-sm font-medium ${getScoreColor(score)}`}>
                  {score.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}