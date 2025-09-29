'use client';

interface LegendItem {
  id: string;
  label: string;
  colorClass: string;
  helper?: string;
}

interface TimetableLegendProps {
  items: LegendItem[];
}

export default function TimetableLegend({ items }: TimetableLegendProps) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-3 text-sm text-gray-600">
      {items.map((item) => (
        <span
          key={item.id}
          className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 shadow-sm"
        >
          <span className={`h-2.5 w-2.5 rounded-full ${item.colorClass}`} />
          <span className="font-medium text-gray-700">{item.label}</span>
          {item.helper && <span className="text-xs text-gray-400">{item.helper}</span>}
        </span>
      ))}
    </div>
  );
}
