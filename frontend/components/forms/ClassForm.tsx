'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface ClassFormData {
  grade: string;
  section: string;
  stream?: string;
  studentCount: number;
  homeRoom?: string;
  classTeacherId?: string;
}

interface ClassFormProps {
  onSubmit: (data: ClassFormData) => void;
  teachers?: { id: string; name: string }[];
  initialData?: Partial<ClassFormData>;
  isLoading?: boolean;
}

export const ClassForm: React.FC<ClassFormProps> = ({
  onSubmit,
  teachers = [],
  initialData,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<ClassFormData>({
    grade: initialData?.grade || '',
    section: initialData?.section || '',
    stream: initialData?.stream || '',
    studentCount: initialData?.studentCount || 30,
    homeRoom: initialData?.homeRoom || '',
    classTeacherId: initialData?.classTeacherId || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const gradeOptions = Array.from({ length: 12 }, (_, i) => ({
    value: (i + 1).toString(),
    label: `Grade ${i + 1}`,
  }));

  const sectionOptions = ['A', 'B', 'C', 'D', 'E'].map(s => ({
    value: s,
    label: `Section ${s}`,
  }));

  const streamOptions = [
    { value: '', label: 'None' },
    { value: 'SCIENCE', label: 'Science' },
    { value: 'COMMERCE', label: 'Commerce' },
    { value: 'ARTS', label: 'Arts' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!formData.grade) {
      newErrors.grade = 'Grade is required';
    }

    if (!formData.section) {
      newErrors.section = 'Section is required';
    }

    if (formData.studentCount < 1 || formData.studentCount > 60) {
      newErrors.studentCount = 'Student count must be between 1 and 60';
    }

    // Stream is required for grades 11 and 12
    const gradeNum = parseInt(formData.grade);
    if (gradeNum >= 11 && !formData.stream) {
      newErrors.stream = 'Stream is required for grades 11 and 12';
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

    // Auto-clear stream for grades below 11
    if (field === 'grade') {
      const gradeNum = parseInt(value);
      if (gradeNum < 11) {
        setFormData(prev => ({
          ...prev,
          stream: '',
        }));
      }
    }
  };

  const showStreamField = formData.grade && parseInt(formData.grade) >= 11;

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card title="Class Information">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Grade"
              value={formData.grade}
              onChange={(e) => handleInputChange('grade', e.target.value)}
              options={gradeOptions}
              error={errors.grade}
              required
            />
            <Select
              label="Section"
              value={formData.section}
              onChange={(e) => handleInputChange('section', e.target.value)}
              options={sectionOptions}
              error={errors.section}
              required
            />
            {showStreamField && (
              <Select
                label="Stream"
                value={formData.stream}
                onChange={(e) => handleInputChange('stream', e.target.value)}
                options={streamOptions}
                error={errors.stream}
                required
                helperText="Required for grades 11 and 12"
              />
            )}
            <Input
              type="number"
              label="Number of Students"
              value={formData.studentCount}
              onChange={(e) => handleInputChange('studentCount', parseInt(e.target.value))}
              error={errors.studentCount}
              min="1"
              max="60"
              required
            />
            <Input
              label="Home Room"
              value={formData.homeRoom}
              onChange={(e) => handleInputChange('homeRoom', e.target.value)}
              placeholder="Room 101"
            />
            {teachers.length > 0 && (
              <Select
                label="Class Teacher"
                value={formData.classTeacherId}
                onChange={(e) => handleInputChange('classTeacherId', e.target.value)}
                options={teachers.map(t => ({
                  value: t.id,
                  label: t.name,
                }))}
              />
            )}
          </div>
        </Card>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Update Class' : 'Create Class'}
          </Button>
        </div>
      </div>
    </form>
  );
};