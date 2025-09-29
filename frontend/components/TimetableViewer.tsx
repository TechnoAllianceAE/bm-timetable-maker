'use client';

import { useEffect, useState } from 'react';
import { timeslotAPI } from '@/lib/api';

interface TimeSlot {
  id: string;
  dayOfWeek: number;
  periodNumber: number;
  startTime: string;
  endTime: string;
  classId: string;
  teacherId: string;
  subjectId: string;
  roomId: string;
  class?: { name: string };
  teacher?: { name: string };
  subject?: { name: string };
  room?: { name: string; roomNumber: string };
}

interface TimetableViewerProps {
  timetableId: string;
  viewMode?: 'class' | 'teacher' | 'room';
  filterById?: string;
}

export default function TimetableViewer({
  timetableId,
  viewMode = 'class',
  filterById,
}: TimetableViewerProps) {
  const [timeslots, setTimeslots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const periods = Array.from({ length: 8 }, (_, i) => i + 1);

  useEffect(() => {
    if (timetableId) {
      fetchTimeslots();
    }
  }, [timetableId]);

  const fetchTimeslots = async () => {
    try {
      const response = await timeslotAPI.list(timetableId);
      setTimeslots(response.data);
    } catch (error) {
      console.error('Failed to fetch timeslots:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSlot = (day: number, period: number) => {
    return timeslots.find(
      (slot) => slot.dayOfWeek === day && slot.periodNumber === period
    );
  };

  const getCellContent = (slot: TimeSlot | undefined) => {
    if (!slot) return { primary: '-', secondary: '', tertiary: '' };

    switch (viewMode) {
      case 'teacher':
        return {
          primary: slot.subject?.name || 'N/A',
          secondary: slot.class?.name || '',
          tertiary: slot.room?.roomNumber || '',
        };
      case 'room':
        return {
          primary: slot.subject?.name || 'N/A',
          secondary: slot.class?.name || '',
          tertiary: slot.teacher?.name || '',
        };
      default: // class view
        return {
          primary: slot.subject?.name || 'N/A',
          secondary: slot.teacher?.name || '',
          tertiary: slot.room?.roomNumber || '',
        };
    }
  };

  const getCellColor = (slot: TimeSlot | undefined) => {
    if (!slot) return 'bg-gray-50';

    const colors = [
      'bg-blue-100',
      'bg-green-100',
      'bg-yellow-100',
      'bg-purple-100',
      'bg-pink-100',
      'bg-indigo-100',
      'bg-red-100',
      'bg-orange-100',
    ];

    const hash = slot.subjectId?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0;
    return colors[hash % colors.length];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading timetable...</div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Period
            </th>
            {days.map((day) => (
              <th
                key={day}
                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {periods.map((period) => (
            <tr key={period}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                Period {period}
              </td>
              {days.map((_, dayIndex) => {
                const slot = getSlot(dayIndex + 1, period);
                const content = getCellContent(slot);
                const color = getCellColor(slot);

                return (
                  <td
                    key={dayIndex}
                    className={`px-2 py-2 text-center ${color} border border-gray-200`}
                  >
                    <div className="min-h-[60px] flex flex-col justify-center">
                      <div className="font-medium text-sm text-gray-900">
                        {content.primary}
                      </div>
                      {content.secondary && (
                        <div className="text-xs text-gray-600 mt-1">
                          {content.secondary}
                        </div>
                      )}
                      {content.tertiary && (
                        <div className="text-xs text-gray-500">
                          {content.tertiary}
                        </div>
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}