'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface SchoolFormData {
  name: string;
  address: string;
  subscriptionTier: string;
  settings: {
    workingDays: string[];
    startTime: string;
    endTime: string;
    lunchBreakStart: string;
    lunchBreakEnd: string;
    periodsPerDay: number;
    periodDuration: number;
  };
}

interface SchoolFormProps {
  onSubmit: (data: SchoolFormData) => void;
  initialData?: Partial<SchoolFormData>;
  isLoading?: boolean;
}

export const SchoolForm: React.FC<SchoolFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<SchoolFormData>({
    name: initialData?.name || '',
    address: initialData?.address || '',
    subscriptionTier: initialData?.subscriptionTier || 'BASIC',
    settings: {
      workingDays: initialData?.settings?.workingDays || ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      startTime: initialData?.settings?.startTime || '08:00',
      endTime: initialData?.settings?.endTime || '15:00',
      lunchBreakStart: initialData?.settings?.lunchBreakStart || '12:00',
      lunchBreakEnd: initialData?.settings?.lunchBreakEnd || '13:00',
      periodsPerDay: initialData?.settings?.periodsPerDay || 8,
      periodDuration: initialData?.settings?.periodDuration || 45,
    },
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!formData.name) {
      newErrors.name = 'School name is required';
    }

    if (formData.settings.workingDays.length === 0) {
      newErrors.workingDays = 'At least one working day must be selected';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit(formData);
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    setErrors(prev => ({
      ...prev,
      [field]: '',
    }));
  };

  const handleSettingsChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      settings: {
        ...prev.settings,
        [field]: value,
      },
    }));
  };

  const toggleWorkingDay = (day: string) => {
    const currentDays = formData.settings.workingDays;
    const newDays = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day];

    handleSettingsChange('workingDays', newDays);
    setErrors(prev => ({
      ...prev,
      workingDays: '',
    }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card title="Basic Information">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="School Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={errors.name}
              required
              placeholder="St. Mary's High School"
            />
            <Select
              label="Subscription Tier"
              value={formData.subscriptionTier}
              onChange={(e) => handleInputChange('subscriptionTier', e.target.value)}
              options={[
                { value: 'BASIC', label: 'Basic' },
                { value: 'PREMIUM', label: 'Premium' },
                { value: 'ENTERPRISE', label: 'Enterprise' },
              ]}
            />
          </div>
          <Input
            label="Address"
            value={formData.address}
            onChange={(e) => handleInputChange('address', e.target.value)}
            placeholder="123 Main Street, New York, NY 10001"
          />
        </Card>

        <Card title="Schedule Settings">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Working Days
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {weekdays.map(day => (
                  <label key={day} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.settings.workingDays.includes(day)}
                      onChange={() => toggleWorkingDay(day)}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm">{day}</span>
                  </label>
                ))}
              </div>
              {errors.workingDays && (
                <p className="mt-1 text-sm text-red-600">{errors.workingDays}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="time"
                label="School Start Time"
                value={formData.settings.startTime}
                onChange={(e) => handleSettingsChange('startTime', e.target.value)}
                required
              />
              <Input
                type="time"
                label="School End Time"
                value={formData.settings.endTime}
                onChange={(e) => handleSettingsChange('endTime', e.target.value)}
                required
              />
              <Input
                type="time"
                label="Lunch Break Start"
                value={formData.settings.lunchBreakStart}
                onChange={(e) => handleSettingsChange('lunchBreakStart', e.target.value)}
                required
              />
              <Input
                type="time"
                label="Lunch Break End"
                value={formData.settings.lunchBreakEnd}
                onChange={(e) => handleSettingsChange('lunchBreakEnd', e.target.value)}
                required
              />
              <Input
                type="number"
                label="Periods Per Day"
                value={formData.settings.periodsPerDay}
                onChange={(e) => handleSettingsChange('periodsPerDay', parseInt(e.target.value))}
                min="1"
                max="12"
                required
              />
              <Input
                type="number"
                label="Period Duration (minutes)"
                value={formData.settings.periodDuration}
                onChange={(e) => handleSettingsChange('periodDuration', parseInt(e.target.value))}
                min="30"
                max="90"
                required
              />
            </div>
          </div>
        </Card>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Update School' : 'Create School'}
          </Button>
        </div>
      </div>
    </form>
  );
};