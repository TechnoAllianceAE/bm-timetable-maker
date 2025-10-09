'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { schoolAPI } from '@/lib/api';

interface School {
  id: string;
  name: string;
  address: string | null;
  contactEmail: string | null;
  contactPhone: string | null;
  principalName: string | null;
  totalStudents: number | null;
  academicYearStart: string | null;
  academicYearEnd: string | null;
  settings: string | null;
  createdAt: string;
}

export default function SchoolsPage() {
  const [schools, setSchools] = useState<School[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSchool, setEditingSchool] = useState<School | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    contactEmail: '',
    contactPhone: '',
    principalName: '',
    totalStudents: '',
    academicYearStart: '',
    academicYearEnd: '',
  });

  useEffect(() => {
    fetchSchools();
  }, []);

  const fetchSchools = async () => {
    try {
      const response = await schoolAPI.list();
      setSchools(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch schools:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        totalStudents: formData.totalStudents ? parseInt(formData.totalStudents) : null,
      };

      if (editingSchool) {
        await schoolAPI.update(editingSchool.id, payload);
        alert('✅ School updated successfully');
      } else {
        await schoolAPI.create(payload);
        alert('✅ School created successfully');
      }
      fetchSchools();
      setShowModal(false);
      resetForm();
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`❌ Failed to save school: ${errorMessage}`);
      console.error('Failed to save school:', error);
    }
  };

  const handleEdit = (school: School) => {
    setEditingSchool(school);
    setFormData({
      name: school.name,
      address: school.address || '',
      contactEmail: school.contactEmail || '',
      contactPhone: school.contactPhone || '',
      principalName: school.principalName || '',
      totalStudents: school.totalStudents?.toString() || '',
      academicYearStart: school.academicYearStart ? new Date(school.academicYearStart).toISOString().split('T')[0] : '',
      academicYearEnd: school.academicYearEnd ? new Date(school.academicYearEnd).toISOString().split('T')[0] : '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this school?')) {
      try {
        await schoolAPI.delete(id);
        alert('✅ School deleted successfully');
        fetchSchools();
      } catch (error: any) {
        const errorMessage = error.response?.data?.message || error.message || 'Unknown error occurred';
        alert(`❌ Failed to delete school: ${errorMessage}`);
        console.error('Failed to delete school:', error);
      }
    }
  };

  const handleClearData = async (id: string, schoolName: string) => {
    const confirmation = confirm(
      `⚠️ WARNING: This will permanently delete ALL data for "${schoolName}" including:\n\n` +
      `• All Teachers\n` +
      `• All Classes\n` +
      `• All Subjects\n` +
      `• All Rooms\n` +
      `• All Timetables\n` +
      `• All Time Slots\n` +
      `• All Academic Years\n\n` +
      `This action CANNOT be undone!\n\n` +
      `Are you absolutely sure you want to proceed?`
    );

    if (confirmation) {
      const doubleConfirmation = confirm(
        `🚨 FINAL CONFIRMATION\n\n` +
        `Type the school name to confirm: "${schoolName}"\n\n` +
        `Click OK only if you're 100% certain you want to delete ALL data for this school.`
      );

      if (doubleConfirmation) {
        try {
          const response = await schoolAPI.deleteSchoolData(id);
          const data = response.data;
          const counts = data.deletedCounts || {};

          alert(
            `✅ ${data.message || 'Successfully cleared all data!'}\n\n` +
            `Deleted:\n` +
            `• ${counts.deletedTeachers || 0} Teachers\n` +
            `• ${counts.deletedClasses || 0} Classes\n` +
            `• ${counts.deletedSubjects || 0} Subjects\n` +
            `• ${counts.deletedRooms || 0} Rooms\n` +
            `• ${counts.deletedTimetables || 0} Timetables\n` +
            `• ${counts.deletedEntries || 0} Timetable Entries\n` +
            `• ${counts.deletedTimeSlots || 0} Time Slots\n` +
            `• ${counts.deletedRequirements || 0} Subject Requirements\n` +
            `• ${counts.deletedAcademicYears || 0} Academic Years`
          );
          fetchSchools();
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Unknown error occurred';
          alert(`❌ Failed to clear school data: ${errorMessage}`);
          console.error('Failed to clear school data:', error);
        }
      }
    }
  };

  const resetForm = () => {
    setEditingSchool(null);
    setFormData({
      name: '',
      address: '',
      contactEmail: '',
      contactPhone: '',
      principalName: '',
      totalStudents: '',
      academicYearStart: '',
      academicYearEnd: '',
    });
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Schools</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage schools in the system
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add School
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading schools...</div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {schools.map((school) => (
                <li key={school.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <div className="text-lg font-medium text-blue-600">
                            {school.name}
                          </div>
                        </div>
                        <div className="mt-2">
                          <p className="flex items-center text-sm text-gray-500">
                            📍 {school.address || 'No address provided'}
                          </p>
                        </div>
                      </div>
                      <div className="ml-4 flex-shrink-0 flex space-x-2">
                        <button
                          onClick={() => handleEdit(school)}
                          className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleClearData(school.id, school.name)}
                          className="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600"
                          title="Clear all data (teachers, classes, subjects, rooms, timetables)"
                        >
                          Clear Data
                        </button>
                        <button
                          onClick={() => handleDelete(school.id)}
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
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold mb-4">
                {editingSchool ? 'Edit School' : 'Add School'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    School Name
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
                    Address
                  </label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) =>
                      setFormData({ ...formData, address: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    value={formData.contactEmail}
                    onChange={(e) =>
                      setFormData({ ...formData, contactEmail: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.contactPhone}
                    onChange={(e) =>
                      setFormData({ ...formData, contactPhone: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Principal Name
                  </label>
                  <input
                    type="text"
                    value={formData.principalName}
                    onChange={(e) =>
                      setFormData({ ...formData, principalName: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Total Students
                  </label>
                  <input
                    type="number"
                    value={formData.totalStudents}
                    onChange={(e) =>
                      setFormData({ ...formData, totalStudents: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Academic Year Start
                  </label>
                  <input
                    type="date"
                    value={formData.academicYearStart}
                    onChange={(e) =>
                      setFormData({ ...formData, academicYearStart: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Academic Year End
                  </label>
                  <input
                    type="date"
                    value={formData.academicYearEnd}
                    onChange={(e) =>
                      setFormData({ ...formData, academicYearEnd: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
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
                    {editingSchool ? 'Update' : 'Create'}
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