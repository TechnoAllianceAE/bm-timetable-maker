'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface TeacherFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  subjects: string[];
  maxPeriodsPerDay: number;
  maxPeriodsPerWeek: number;
  availability: {
    [key: string]: {
      start: string;
      end: string;
      unavailable: string[];
    };
  };
}

interface TeacherFormProps {
  onSubmit: (data: TeacherFormData) => void;
  subjects: { id: string; name: string }[];
  initialData?: Partial<TeacherFormData>;
  isLoading?: boolean;
}

export const TeacherForm: React.FC<TeacherFormProps> = ({
  onSubmit,
  subjects,
  initialData,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<TeacherFormData>({
    firstName: initialData?.firstName || '',
    lastName: initialData?.lastName || '',
    email: initialData?.email || '',
    phone: initialData?.phone || '',
    subjects: initialData?.subjects || [],
    maxPeriodsPerDay: initialData?.maxPeriodsPerDay || 6,
    maxPeriodsPerWeek: initialData?.maxPeriodsPerWeek || 25,
    availability: initialData?.availability || {
      Monday: { start: '08:00', end: '16:00', unavailable: [] },
      Tuesday: { start: '08:00', end: '16:00', unavailable: [] },
      Wednesday: { start: '08:00', end: '16:00', unavailable: [] },
      Thursday: { start: '08:00', end: '16:00', unavailable: [] },
      Friday: { start: '08:00', end: '14:00', unavailable: [] },
    },
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!formData.firstName) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName) {
      newErrors.lastName = 'Last name is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (formData.subjects.length === 0) {
      newErrors.subjects = 'At least one subject must be selected';
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

  const toggleSubject = (subjectId: string) => {
    const currentSubjects = formData.subjects;
    const newSubjects = currentSubjects.includes(subjectId)
      ? currentSubjects.filter(s => s !== subjectId)
      : [...currentSubjects, subjectId];

    handleInputChange('subjects', newSubjects);
  };

  const updateAvailability = (day: string, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      availability: {
        ...prev.availability,
        [day]: {
          ...prev.availability[day],
          [field]: value,
        },
      },
    }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card title="Personal Information">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={formData.firstName}
              onChange={(e) => handleInputChange('firstName', e.target.value)}
              error={errors.firstName}
              required
              placeholder="John"
            />
            <Input
              label="Last Name"
              value={formData.lastName}
              onChange={(e) => handleInputChange('lastName', e.target.value)}
              error={errors.lastName}
              required
              placeholder="Doe"
            />
            <Input
              type="email"
              label="Email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              error={errors.email}
              required
              placeholder="john.doe@example.com"
            />
            <Input
              type="tel"
              label="Phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              placeholder="+1234567890"
            />
          </div>
        </Card>

        <Card title="Teaching Information">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subjects
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {subjects.map(subject => (
                  <label key={subject.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.subjects.includes(subject.id)}
                      onChange={() => toggleSubject(subject.id)}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm">{subject.name}</span>
                  </label>
                ))}
              </div>
              {errors.subjects && (
                <p className="mt-1 text-sm text-red-600">{errors.subjects}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="number"
                label="Max Periods Per Day"
                value={formData.maxPeriodsPerDay}
                onChange={(e) => handleInputChange('maxPeriodsPerDay', parseInt(e.target.value))}
                min="1"
                max="10"
                required
              />
              <Input
                type="number"
                label="Max Periods Per Week"
                value={formData.maxPeriodsPerWeek}
                onChange={(e) => handleInputChange('maxPeriodsPerWeek', parseInt(e.target.value))}
                min="1"
                max="50"
                required
              />
            </div>
          </div>
        </Card>

        <Card title="Availability">
          <div className="space-y-3">
            {weekdays.map(day => (
              <div key={day} className="grid grid-cols-3 gap-3 items-center">
                <span className="font-medium text-sm">{day}</span>
                <Input
                  type="time"
                  value={formData.availability[day]?.start || '08:00'}
                  onChange={(e) => updateAvailability(day, 'start', e.target.value)}
                  placeholder="Start time"
                />
                <Input
                  type="time"
                  value={formData.availability[day]?.end || '16:00'}
                  onChange={(e) => updateAvailability(day, 'end', e.target.value)}
                  placeholder="End time"
                />
              </div>
            ))}
          </div>
        </Card>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Update Teacher' : 'Add Teacher'}
          </Button>
        </div>
      </div>
    </form>
  );
};