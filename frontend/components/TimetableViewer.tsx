'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { timeslotAPI } from '@/lib/api';
import TimetableToolbar from './timetable/TimetableToolbar';
import TimetableLegend from './timetable/TimetableLegend';
import TimetableGrid from './timetable/TimetableGrid';

interface TimeSlot {
  id: string;
  dayOfWeek: number;
  periodNumber: number;
  startTime?: string;
  endTime?: string;
  classId?: string;
  teacherId?: string;
  subjectId?: string;
  roomId?: string;
  class?: { name?: string };
  teacher?: { name?: string };
  subject?: { name?: string };
  room?: { name?: string; roomNumber?: string };
}

interface TimetableViewerProps {
  timetableId: string;
  viewMode?: 'class' | 'teacher' | 'room';
  filterById?: string;
  allowViewSwitching?: boolean;
  allowFilterChange?: boolean;
}

interface ViewOption {
  id: string;
  label: string;
  helper?: string;
}

const defaultDayLabels: Record<number, string> = {
  1: 'Monday',
  2: 'Tuesday',
  3: 'Wednesday',
  4: 'Thursday',
  5: 'Friday',
  6: 'Saturday',
  7: 'Sunday',
};

const colorPalette = [
  'bg-blue-50 border border-blue-100',
  'bg-green-50 border border-green-100',
  'bg-yellow-50 border border-yellow-100',
  'bg-purple-50 border border-purple-100',
  'bg-pink-50 border border-pink-100',
  'bg-indigo-50 border border-indigo-100',
  'bg-red-50 border border-red-100',
  'bg-orange-50 border border-orange-100',
];

const formatTime = (value?: string) => {
  if (!value) return undefined;
  if (value.includes(':')) {
    return value.slice(0, 5);
  }
  return value;
};

const formatTimeRange = (start?: string, end?: string) => {
  const startFormatted = formatTime(start);
  const endFormatted = formatTime(end);

  if (startFormatted && endFormatted) {
    return `${startFormatted} - ${endFormatted}`;
  }

  return startFormatted || endFormatted;
};

const buildColorKey = (slot: TimeSlot) =>
  slot.subjectId || slot.classId || slot.teacherId || slot.roomId || slot.id;

const getFallbackLabel = (prefix: string, id?: string) =>
  id ? `${prefix} ${id.slice(-4)}` : `${prefix} Unknown`;

export default function TimetableViewer({
  timetableId,
  viewMode = 'class',
  filterById,
  allowViewSwitching = true,
  allowFilterChange = true,
}: TimetableViewerProps) {
  const [timeslots, setTimeslots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentView, setCurrentView] = useState<'class' | 'teacher' | 'room'>(viewMode);
  const [currentFilterId, setCurrentFilterId] = useState<string | undefined>(filterById);

  useEffect(() => {
    setCurrentView(viewMode);
  }, [viewMode]);

  useEffect(() => {
    setCurrentFilterId(filterById);
  }, [filterById]);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const fetchTimeslots = async () => {
      try {
        console.log('🔍 [TimetableViewer] Fetching entries for timetable ID:', timetableId);
        const response = await timeslotAPI.list(timetableId);
        console.log('📦 [TimetableViewer] API Response:', response);
        console.log('📊 [TimetableViewer] Response data:', response.data);

        if (!isMounted) return;
        // Backend returns { data: [...] }, so we need to access response.data.data
        const rawData = response.data?.data || response.data || [];
        const data = Array.isArray(rawData) ? rawData : [];
        console.log('✅ [TimetableViewer] Processed data array length:', data.length);
        console.log('📋 [TimetableViewer] First 3 entries:', data.slice(0, 3));

        setTimeslots(data);
      } catch (err) {
        console.error('❌ [TimetableViewer] Failed to fetch timeslots:', err);
        if (isMounted) {
          setError('Unable to load timetable data right now.');
          setTimeslots([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (timetableId) {
      console.log('🚀 [TimetableViewer] Starting fetch for timetable ID:', timetableId);
      fetchTimeslots();
    } else {
      console.warn('⚠️ [TimetableViewer] No timetable ID provided');
      setTimeslots([]);
      setLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [timetableId]);

  const dayConfig = useMemo(() => {
    const uniqueDays = Array.from(new Set(timeslots.map((slot) => slot.dayOfWeek))).sort((a, b) => a - b);
    const fallback = uniqueDays.length ? uniqueDays : [1, 2, 3, 4, 5];

    return fallback.map((day) => ({
      value: day,
      label: defaultDayLabels[day] || `Day ${day}`,
    }));
  }, [timeslots]);

  const periodConfig = useMemo(() => {
    if (!timeslots.length) {
      return Array.from({ length: 8 }, (_, index) => ({ number: index + 1 }));
    }

    const map = new Map<number, { number: number; startTime?: string; endTime?: string }>();

    timeslots.forEach((slot) => {
      if (!slot.periodNumber) return;
      if (!map.has(slot.periodNumber)) {
        map.set(slot.periodNumber, {
          number: slot.periodNumber,
          startTime: formatTime(slot.startTime),
          endTime: formatTime(slot.endTime),
        });
      }
    });

    return Array.from(map.values()).sort((a, b) => a.number - b.number);
  }, [timeslots]);

  const viewOptions = useMemo(() => {
    const buildOptions = (type: 'class' | 'teacher' | 'room') => {
      const optionMap = new Map<string, ViewOption>();

      timeslots.forEach((slot) => {
        if (type === 'class' && slot.classId) {
          const label = slot.class?.name || getFallbackLabel('Class', slot.classId);
          optionMap.set(slot.classId, { id: slot.classId, label });
        }
        if (type === 'teacher' && slot.teacherId) {
          const label = slot.teacher?.name || getFallbackLabel('Teacher', slot.teacherId);
          optionMap.set(slot.teacherId, { id: slot.teacherId, label });
        }
        if (type === 'room' && slot.roomId) {
          const label =
            slot.room?.roomNumber ||
            slot.room?.name ||
            getFallbackLabel('Room', slot.roomId);
          optionMap.set(slot.roomId, { id: slot.roomId, label });
        }
      });

      return Array.from(optionMap.values()).sort((a, b) => a.label.localeCompare(b.label));
    };

    return {
      class: buildOptions('class'),
      teacher: buildOptions('teacher'),
      room: buildOptions('room'),
    };
  }, [timeslots]);

  useEffect(() => {
    const optionsForView = viewOptions[currentView];
    if (!optionsForView.length) {
      setCurrentFilterId(undefined);
      return;
    }

    const currentExists = currentFilterId && optionsForView.some((option) => option.id === currentFilterId);
    if (!currentExists) {
      setCurrentFilterId(optionsForView[0].id);
    }
  }, [currentView, viewOptions, currentFilterId]);

  const filteredSlots = useMemo(() => {
    if (!currentFilterId) return timeslots;

    switch (currentView) {
      case 'class':
        return timeslots.filter((slot) => slot.classId === currentFilterId);
      case 'teacher':
        return timeslots.filter((slot) => slot.teacherId === currentFilterId);
      case 'room':
        return timeslots.filter((slot) => slot.roomId === currentFilterId);
      default:
        return timeslots;
    }
  }, [timeslots, currentView, currentFilterId]);

  const getSlotContent = useCallback(
    (slot: TimeSlot) => {
      if (!slot) {
        return { primary: '-', secondary: '', tertiary: '' };
      }

      const roomLabel = slot.room?.roomNumber || slot.room?.name;
      const timeLabel = formatTimeRange(slot.startTime, slot.endTime);

      switch (currentView) {
        case 'teacher':
          return {
            primary: slot.subject?.name || 'Subject TBD',
            secondary: slot.class?.name || getFallbackLabel('Class', slot.classId),
            tertiary: roomLabel || timeLabel || '',
          };
        case 'room':
          return {
            primary: slot.subject?.name || slot.class?.name || 'Scheduled Session',
            secondary: slot.class?.name || getFallbackLabel('Class', slot.classId),
            tertiary: slot.teacher?.name || timeLabel || '',
          };
        default:
          return {
            primary: slot.subject?.name || 'Subject TBD',
            secondary: slot.teacher?.name || getFallbackLabel('Teacher', slot.teacherId),
            tertiary: roomLabel || timeLabel || '',
          };
      }
    },
    [currentView]
  );

  const colorAssignments = useMemo(() => {
    const map = new Map<string, string>();
    let colorIndex = 0;

    filteredSlots.forEach((slot) => {
      const key = buildColorKey(slot);
      if (!key) return;
      if (!map.has(key)) {
        map.set(key, colorPalette[colorIndex % colorPalette.length]);
        colorIndex += 1;
      }
    });

    return map;
  }, [filteredSlots]);

  const legendItems = useMemo(() => {
    return Array.from(colorAssignments.entries()).map(([key, colorClass]) => {
      const slot = filteredSlots.find((item) => buildColorKey(item) === key);
      if (!slot) {
        return { id: key, label: key, colorClass };
      }

      const content = getSlotContent(slot);
      return {
        id: key,
        label: content.primary,
        helper: content.secondary,
        colorClass,
      };
    });
  }, [colorAssignments, filteredSlots, getSlotContent]);

  const getSlotColor = useCallback(
    (slot: TimeSlot) => {
      const key = buildColorKey(slot);
      return (key && colorAssignments.get(key)) || 'bg-gray-50';
    },
    [colorAssignments]
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading timetable...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-700">
        {error}
      </div>
    );
  }

  if (!timeslots.length) {
    return (
      <div className="rounded-md border border-gray-200 bg-gray-50 p-6 text-center text-gray-600">
        No timetable data available yet.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <TimetableToolbar
        currentView={currentView}
        onViewChange={(nextView) => {
          if (!allowViewSwitching && nextView !== currentView) return;
          setCurrentView(nextView);
        }}
        options={viewOptions}
        currentFilterId={currentFilterId}
        onFilterChange={(id) => {
          if (!allowFilterChange) return;
          setCurrentFilterId(id);
        }}
        disableViewSwitching={!allowViewSwitching}
        lockFilter={!allowFilterChange}
      />

      <TimetableLegend items={legendItems} />

      <TimetableGrid
        days={dayConfig}
        periods={periodConfig}
        slots={filteredSlots}
        renderSlotContent={getSlotContent}
        getSlotColor={getSlotColor}
      />
    </div>
  );
}
