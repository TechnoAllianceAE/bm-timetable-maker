'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface RoomFormData {
  roomNumber: string;
  building: string;
  floor: string;
  type: string;
  capacity: number;
  facilities: string[];
  isAvailable: boolean;
  description: string;
}

interface RoomFormProps {
  onSubmit: (data: RoomFormData) => void;
  initialData?: Partial<RoomFormData>;
  isLoading?: boolean;
}

export const RoomForm: React.FC<RoomFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<RoomFormData>({
    roomNumber: initialData?.roomNumber || '',
    building: initialData?.building || '',
    floor: initialData?.floor || '',
    type: initialData?.type || 'CLASSROOM',
    capacity: initialData?.capacity || 40,
    facilities: initialData?.facilities || [],
    isAvailable: initialData?.isAvailable !== undefined ? initialData.isAvailable : true,
    description: initialData?.description || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [newFacility, setNewFacility] = useState('');

  const roomTypes = [
    { value: 'CLASSROOM', label: 'Classroom' },
    { value: 'LAB', label: 'Laboratory' },
    { value: 'COMPUTER_LAB', label: 'Computer Lab' },
    { value: 'SCIENCE_LAB', label: 'Science Lab' },
    { value: 'LIBRARY', label: 'Library' },
    { value: 'AUDITORIUM', label: 'Auditorium' },
    { value: 'GYMNASIUM', label: 'Gymnasium' },
    { value: 'MUSIC_ROOM', label: 'Music Room' },
    { value: 'ART_ROOM', label: 'Art Room' },
    { value: 'SPECIAL', label: 'Special Purpose' },
  ];

  const commonFacilities = [
    'Projector',
    'Whiteboard',
    'Smart Board',
    'Air Conditioning',
    'Computer',
    'Audio System',
    'Laboratory Equipment',
    'Sports Equipment',
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!formData.roomNumber) {
      newErrors.roomNumber = 'Room number is required';
    }

    if (formData.capacity < 1 || formData.capacity > 200) {
      newErrors.capacity = 'Capacity must be between 1 and 200';
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

  const toggleFacility = (facility: string) => {
    const currentFacilities = formData.facilities;
    const newFacilities = currentFacilities.includes(facility)
      ? currentFacilities.filter(f => f !== facility)
      : [...currentFacilities, facility];

    handleInputChange('facilities', newFacilities);
  };

  const addCustomFacility = () => {
    if (newFacility.trim() && !formData.facilities.includes(newFacility.trim())) {
      handleInputChange('facilities', [...formData.facilities, newFacility.trim()]);
      setNewFacility('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <Card title="Room Information">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Room Number"
              value={formData.roomNumber}
              onChange={(e) => handleInputChange('roomNumber', e.target.value)}
              error={errors.roomNumber}
              required
              placeholder="101"
            />
            <Input
              label="Building"
              value={formData.building}
              onChange={(e) => handleInputChange('building', e.target.value)}
              placeholder="Building A"
            />
            <Input
              label="Floor"
              value={formData.floor}
              onChange={(e) => handleInputChange('floor', e.target.value)}
              placeholder="Ground Floor"
            />
            <Select
              label="Room Type"
              value={formData.type}
              onChange={(e) => handleInputChange('type', e.target.value)}
              options={roomTypes}
              required
            />
            <Input
              type="number"
              label="Capacity"
              value={formData.capacity}
              onChange={(e) => handleInputChange('capacity', parseInt(e.target.value))}
              error={errors.capacity}
              min="1"
              max="200"
              required
            />
            <div className="flex items-end">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.isAvailable}
                  onChange={(e) => handleInputChange('isAvailable', e.target.checked)}
                  className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Room is Available</span>
              </label>
            </div>
          </div>
        </Card>

        <Card title="Facilities">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Common Facilities
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {commonFacilities.map(facility => (
                  <label key={facility} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.facilities.includes(facility)}
                      onChange={() => toggleFacility(facility)}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm">{facility}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Add Custom Facility
              </label>
              <div className="flex gap-2">
                <Input
                  value={newFacility}
                  onChange={(e) => setNewFacility(e.target.value)}
                  placeholder="Enter facility name"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addCustomFacility();
                    }
                  }}
                />
                <Button type="button" onClick={addCustomFacility} variant="secondary">
                  Add
                </Button>
              </div>
            </div>

            {formData.facilities.filter(f => !commonFacilities.includes(f)).length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Facilities
                </label>
                <div className="flex flex-wrap gap-2">
                  {formData.facilities
                    .filter(f => !commonFacilities.includes(f))
                    .map(facility => (
                      <span
                        key={facility}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                      >
                        {facility}
                        <button
                          type="button"
                          onClick={() => toggleFacility(facility)}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card title="Additional Information">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Additional information about the room..."
            />
          </div>
        </Card>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Update Room' : 'Create Room'}
          </Button>
        </div>
      </div>
    </form>
  );
};