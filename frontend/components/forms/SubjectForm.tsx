'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface SubjectFormData {
  name: string;
  code: string;
  type: string;
  periodsPerWeek: number;
  credits: number;
  requiresLab: boolean;
  requiresSpecialRoom: boolean;
  description: string;
}

interface SubjectFormProps {
  onSubmit: (data: SubjectFormData) => void;
  initialData?: Partial<SubjectFormData>;
  isLoading?: boolean;
}

export const SubjectForm: React.FC<SubjectFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<SubjectFormData>({
    name: initialData?.name || '',
    code: initialData?.code || '',
    type: initialData?.type || 'CORE',
    periodsPerWeek: initialData?.periodsPerWeek || 4,
    credits: initialData?.credits || 2,
    requiresLab: initialData?.requiresLab || false,
    requiresSpecialRoom: initialData?.requiresSpecialRoom || false,
    description: initialData?.description || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const subjectTypes = [
    { value: 'CORE', label: 'Core Subject' },
    { value: 'ELECTIVE', label: 'Elective' },
    { value: 'LAB', label: 'Laboratory' },
    { value: 'ACTIVITY', label: 'Activity' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!formData.name) {
      newErrors.name = 'Subject name is required';
    }

    if (!formData.code) {
      newErrors.code = 'Subject code is required';
    }

    if (formData.periodsPerWeek < 1 || formData.periodsPerWeek > 10) {
      newErrors.periodsPerWeek = 'Periods per week must be between 1 and 10';
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

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card title="Subject Information">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Subject Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={errors.name}
              required
              placeholder="Mathematics"
            />
            <Input
              label="Subject Code"
              value={formData.code}
              onChange={(e) => handleInputChange('code', e.target.value.toUpperCase())}
              error={errors.code}
              required
              placeholder="MATH"
            />
            <Select
              label="Subject Type"
              value={formData.type}
              onChange={(e) => handleInputChange('type', e.target.value)}
              options={subjectTypes}
              required
            />
            <Input
              type="number"
              label="Periods Per Week"
              value={formData.periodsPerWeek}
              onChange={(e) => handleInputChange('periodsPerWeek', parseInt(e.target.value))}
              error={errors.periodsPerWeek}
              min="1"
              max="10"
              required
            />
            <Input
              type="number"
              label="Credit Hours"
              value={formData.credits}
              onChange={(e) => handleInputChange('credits', parseInt(e.target.value))}
              min="1"
              max="10"
            />
          </div>

          <div className="mt-4 space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.requiresLab}
                onChange={(e) => handleInputChange('requiresLab', e.target.checked)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Requires Laboratory</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.requiresSpecialRoom}
                onChange={(e) => handleInputChange('requiresSpecialRoom', e.target.checked)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Requires Special Room</span>
            </label>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Advanced mathematics covering algebra, geometry, and calculus..."
            />
          </div>
        </Card>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Update Subject' : 'Create Subject'}
          </Button>
        </div>
      </div>
    </form>
  );
};