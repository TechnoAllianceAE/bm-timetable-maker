'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { subjectAPI } from '@/lib/api';

interface Subject {
  id: string;
  name: string;
  department?: string;
  credits: number;
  minPeriodsPerWeek?: number;
  maxPeriodsPerWeek?: number;
  prepTime?: number;
  correctionWorkload?: number;
  requiresLab: boolean;
  schoolId: string;
  createdAt: string;
}

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    department: '',
    credits: 4,
    minPeriodsPerWeek: 4,
    maxPeriodsPerWeek: 6,
    prepTime: 60,
    correctionWorkload: 0.5,
    requiresLab: false,
    schoolId: '',
  });

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await subjectAPI.list();
      setSubjects(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Get schoolId from localStorage
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const schoolId = user.schoolId || 'default-school-id';

      const dataToSend = {
        ...formData,
        schoolId,
      };

      if (editingSubject) {
        await subjectAPI.update(editingSubject.id, dataToSend);
      } else {
        await subjectAPI.create(dataToSend);
      }
      fetchSubjects();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save subject:', error);
      alert('Failed to save subject. Please check the console for details.');
    }
  };

  const handleEdit = (subject: Subject) => {
    setEditingSubject(subject);
    setFormData({
      name: subject.name,
      department: subject.department || '',
      credits: subject.credits,
      minPeriodsPerWeek: subject.minPeriodsPerWeek || 4,
      maxPeriodsPerWeek: subject.maxPeriodsPerWeek || 6,
      prepTime: subject.prepTime || 60,
      correctionWorkload: subject.correctionWorkload || 0.5,
      requiresLab: subject.requiresLab,
      schoolId: subject.schoolId,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this subject?')) {
      try {
        await subjectAPI.delete(id);
        fetchSubjects();
      } catch (error) {
        console.error('Failed to delete subject:', error);
      }
    }
  };

  const resetForm = () => {
    setEditingSubject(null);
    setFormData({
      name: '',
      department: '',
      credits: 4,
      minPeriodsPerWeek: 4,
      maxPeriodsPerWeek: 6,
      prepTime: 60,
      correctionWorkload: 0.5,
      requiresLab: false,
      schoolId: '',
    });
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Subjects</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage subjects in the system
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add Subject
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading subjects...</div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {subjects.length === 0 ? (
                <li className="px-4 py-8 text-center text-gray-500">
                  No subjects found. Click "Add Subject" to create one.
                </li>
              ) : (
                subjects.map((subject) => (
                  <li key={subject.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <div className="text-lg font-medium text-blue-600">
                              {subject.name}
                            </div>
                            {subject.requiresLab && (
                              <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                                Lab
                              </span>
                            )}
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex sm:space-x-6">
                              {subject.department && (
                                <p className="flex items-center text-sm text-gray-500">
                                  Dept: {subject.department}
                                </p>
                              )}
                              <p className="flex items-center text-sm text-gray-500">
                                Credits: {subject.credits}
                              </p>
                              <p className="flex items-center text-sm text-gray-500">
                                Periods/Week: {subject.minPeriodsPerWeek || 0}-{subject.maxPeriodsPerWeek || 0}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="ml-4 flex-shrink-0 flex space-x-2">
                          <button
                            onClick={() => handleEdit(subject)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(subject.id)}
                            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold mb-4">
                {editingSubject ? 'Edit Subject' : 'Add Subject'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Subject Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="e.g., Mathematics"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Department (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) =>
                      setFormData({ ...formData, department: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="e.g., Science, Arts"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Credits
                    </label>
                    <input
                      type="number"
                      required
                      min="1"
                      max="10"
                      value={formData.credits}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          credits: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Prep Time (min)
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.prepTime}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          prepTime: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Min Periods/Week
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={formData.minPeriodsPerWeek}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          minPeriodsPerWeek: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Max Periods/Week
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={formData.maxPeriodsPerWeek}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          maxPeriodsPerWeek: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="requiresLab"
                    checked={formData.requiresLab}
                    onChange={(e) =>
                      setFormData({ ...formData, requiresLab: e.target.checked })
                    }
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="requiresLab" className="ml-2 block text-sm text-gray-900">
                    Requires Lab
                  </label>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    {editingSubject ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}