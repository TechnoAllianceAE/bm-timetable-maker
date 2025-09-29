'use client';

interface ViewOption {
  id: string;
  label: string;
  helper?: string;
}

interface TimetableToolbarProps {
  currentView: 'class' | 'teacher' | 'room';
  onViewChange: (view: 'class' | 'teacher' | 'room') => void;
  options: {
    class: ViewOption[];
    teacher: ViewOption[];
    room: ViewOption[];
  };
  currentFilterId?: string;
  onFilterChange: (id: string) => void;
  disableViewSwitching?: boolean;
  lockFilter?: boolean;
}

const viewLabels: Record<'class' | 'teacher' | 'room', string> = {
  class: 'Class View',
  teacher: 'Teacher View',
  room: 'Room View',
};

export default function TimetableToolbar({
  currentView,
  onViewChange,
  options,
  currentFilterId,
  onFilterChange,
  disableViewSwitching = false,
  lockFilter = false,
}: TimetableToolbarProps) {
  const filterOptions = options[currentView] || [];
  const hasMultipleFilters = filterOptions.length > 1;

  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-600">View mode:</span>
        <div className="inline-flex rounded-md shadow-sm border border-gray-200 overflow-hidden">
          {(['class', 'teacher', 'room'] as const).map((view) => (
            <button
              key={view}
              type="button"
              onClick={() => onViewChange(view)}
              disabled={disableViewSwitching && view !== currentView}
              className={`px-3 py-1.5 text-sm transition-colors ${
                currentView === view
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              } ${disableViewSwitching && view !== currentView ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {viewLabels[view]}
            </button>
          ))}
        </div>
      </div>

      {filterOptions.length > 0 && (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-600">
            {viewLabels[currentView].replace('View', '')}
          </label>
          <select
            value={currentFilterId}
            onChange={(event) => onFilterChange(event.target.value)}
            className="block w-full rounded-md border-gray-300 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
            disabled={lockFilter || !hasMultipleFilters}
          >
            {filterOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          {(lockFilter || (!hasMultipleFilters && filterOptions.length === 1)) && (
            <p className="text-xs text-gray-500">
              {lockFilter
                ? 'Viewing options locked for your role.'
                : `Only one ${viewLabels[currentView].toLowerCase()} available.`}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
