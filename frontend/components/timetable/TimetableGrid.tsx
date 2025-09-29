'use client';

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

interface DayConfig {
  label: string;
  value: number;
}

interface PeriodConfig {
  number: number;
  startTime?: string;
  endTime?: string;
}

interface TimetableGridProps {
  days: DayConfig[];
  periods: PeriodConfig[];
  slots: TimeSlot[];
  renderSlotContent: (slot: TimeSlot) => {
    primary: string;
    secondary?: string;
    tertiary?: string;
  };
  getSlotColor: (slot: TimeSlot) => string;
}

export default function TimetableGrid({
  days,
  periods,
  slots,
  renderSlotContent,
  getSlotColor,
}: TimetableGridProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Period
            </th>
            {days.map((day) => (
              <th
                key={day.value}
                className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                {day.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {periods.map((period) => (
            <tr key={period.number} className="align-top">
              <td className="px-4 py-4 text-sm font-medium text-gray-900 w-36">
                <div>Period {period.number}</div>
                {(period.startTime || period.endTime) && (
                  <div className="mt-1 text-xs text-gray-500">
                    {[period.startTime, period.endTime].filter(Boolean).join(' - ')}
                  </div>
                )}
              </td>
              {days.map((day) => {
                const cellSlots = slots.filter(
                  (slot) => slot.dayOfWeek === day.value && slot.periodNumber === period.number
                );

                if (!cellSlots.length) {
                  return (
                    <td
                      key={`${day.value}-${period.number}`}
                      className="px-2 py-4 text-center text-xs text-gray-400 border border-gray-100"
                    >
                      Free
                    </td>
                  );
                }

                return (
                  <td
                    key={`${day.value}-${period.number}`}
                    className="px-2 py-2 border border-gray-100"
                  >
                    <div className="flex flex-col gap-2">
                      {cellSlots.map((slot) => {
                        const content = renderSlotContent(slot);
                        const colorClass = getSlotColor(slot);
                        return (
                          <div
                            key={slot.id}
                            className={`rounded-lg px-3 py-2 text-center shadow-sm ${colorClass}`}
                          >
                            <div className="text-sm font-semibold text-gray-900">
                              {content.primary || '—'}
                            </div>
                            {content.secondary && (
                              <div className="text-xs text-gray-700 mt-1">
                                {content.secondary}
                              </div>
                            )}
                            {content.tertiary && (
                              <div className="text-xs text-gray-600">
                                {content.tertiary}
                              </div>
                            )}
                          </div>
                        );
                      })}
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
