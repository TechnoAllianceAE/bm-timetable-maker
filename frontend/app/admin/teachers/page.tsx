'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { teacherAPI, schoolAPI, subjectAPI } from '@/lib/api';

interface Teacher {
  id: string;
  name: string;
  email: string;
  phone: string;
  specialization: string;
  yearsOfExperience: number;
  qualification: string;
  schoolId: string;
  school?: { name: string };
  maxHoursPerWeek: number;
  subjectIds: string[];
  subjects?: { id: string; name: string }[];
}

interface School {
  id: string;
  name: string;
}

interface Subject {
  id: string;
  name: string;
}

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    specialization: '',
    yearsOfExperience: 0,
    qualification: '',
    schoolId: '',
    maxHoursPerWeek: 40,
    subjectIds: [] as string[],
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [teachersRes, schoolsRes, subjectsRes] = await Promise.all([
        teacherAPI.list(),
        schoolAPI.list(),
        subjectAPI.list(),
      ]);
      setTeachers(teachersRes.data);
      setSchools(schoolsRes.data);
      setSubjects(subjectsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTeacher) {
        await teacherAPI.update(editingTeacher.id, formData);
      } else {
        await teacherAPI.create(formData);
      }
      fetchData();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save teacher:', error);
    }
  };

  const handleEdit = (teacher: Teacher) => {
    setEditingTeacher(teacher);
    setFormData({
      name: teacher.name,
      email: teacher.email,
      phone: teacher.phone,
      specialization: teacher.specialization,
      yearsOfExperience: teacher.yearsOfExperience,
      qualification: teacher.qualification,
      schoolId: teacher.schoolId,
      maxHoursPerWeek: teacher.maxHoursPerWeek,
      subjectIds: teacher.subjectIds || [],
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this teacher?')) {
      try {
        await teacherAPI.delete(id);
        fetchData();
      } catch (error) {
        console.error('Failed to delete teacher:', error);
      }
    }
  };

  const resetForm = () => {
    setEditingTeacher(null);
    setFormData({
      name: '',
      email: '',
      phone: '',
      specialization: '',
      yearsOfExperience: 0,
      qualification: '',
      schoolId: '',
      maxHoursPerWeek: 40,
      subjectIds: [],
    });
  };

  const toggleSubject = (subjectId: string) => {
    setFormData(prev => ({
      ...prev,
      subjectIds: prev.subjectIds.includes(subjectId)
        ? prev.subjectIds.filter(id => id !== subjectId)
        : [...prev.subjectIds, subjectId]
    }));
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Teachers</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage teachers in the system
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add Teacher
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading teachers...</div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {teachers.map((teacher) => (
                <li key={teacher.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <div className="text-lg font-medium text-blue-600">
                            {teacher.name}
                          </div>
                          <span className="ml-3 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                            {teacher.qualification}
                          </span>
                        </div>
                        <div className="mt-2 sm:flex sm:justify-between">
                          <div className="sm:flex sm:space-x-6">
                            <p className="flex items-center text-sm text-gray-500">
                              📧 {teacher.email}
                            </p>
                            <p className="flex items-center text-sm text-gray-500">
                              📞 {teacher.phone}
                            </p>
                            <p className="flex items-center text-sm text-gray-500">
                              🏫 {teacher.school?.name || 'N/A'}
                            </p>
                            <p className="flex items-center text-sm text-gray-500">
                              📚 {teacher.specialization}
                            </p>
                          </div>
                          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                            <p>⏰ Max {teacher.maxHoursPerWeek} hrs/week</p>
                          </div>
                        </div>
                        {teacher.subjects && teacher.subjects.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-2">
                              {teacher.subjects.map((subject) => (
                                <span
                                  key={subject.id}
                                  className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                                >
                                  {subject.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="ml-4 flex-shrink-0 flex space-x-2">
                        <button
                          onClick={() => handleEdit(teacher)}
                          className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(teacher.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
              <h2 className="text-xl font-semibold mb-4">
                {editingTeacher ? 'Edit Teacher' : 'Add Teacher'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Full Name
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Phone
                    </label>
                    <input
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={(e) =>
                        setFormData({ ...formData, phone: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      School
                    </label>
                    <select
                      required
                      value={formData.schoolId}
                      onChange={(e) =>
                        setFormData({ ...formData, schoolId: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    >
                      <option value="">Select a school</option>
                      {schools.map((school) => (
                        <option key={school.id} value={school.id}>
                          {school.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Specialization
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.specialization}
                      onChange={(e) =>
                        setFormData({ ...formData, specialization: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Qualification
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.qualification}
                      onChange={(e) =>
                        setFormData({ ...formData, qualification: e.target.value })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Years of Experience
                    </label>
                    <input
                      type="number"
                      required
                      value={formData.yearsOfExperience}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          yearsOfExperience: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Max Hours Per Week
                    </label>
                    <input
                      type="number"
                      required
                      value={formData.maxHoursPerWeek}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          maxHoursPerWeek: parseInt(e.target.value),
                        })
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subjects (Select all that apply)
                  </label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded p-2">
                    {subjects.map((subject) => (
                      <label key={subject.id} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.subjectIds.includes(subject.id)}
                          onChange={() => toggleSubject(subject.id)}
                          className="mr-2"
                        />
                        <span className="text-sm">{subject.name}</span>
                      </label>
                    ))}
                  </div>
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
                    {editingTeacher ? 'Update' : 'Create'}
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