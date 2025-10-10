'use client';

import { useEffect, useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { roomAPI } from '@/lib/api';

interface Room {
  id: string;
  name: string;
  code: string;
  capacity: number;
  type: string;
  schoolId: string;
  createdAt: string;
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    capacity: 30,
    type: 'CLASSROOM',
  });

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await roomAPI.list();
      setRooms(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingRoom) {
        await roomAPI.update(editingRoom.id, formData);
      } else {
        await roomAPI.create(formData);
      }
      fetchRooms();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save room:', error);
    }
  };

  const handleEdit = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      name: room.name,
      code: room.code,
      capacity: room.capacity,
      type: room.type,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this room?')) {
      try {
        await roomAPI.delete(id);
        fetchRooms();
      } catch (error) {
        console.error('Failed to delete room:', error);
      }
    }
  };

  const resetForm = () => {
    setEditingRoom(null);
    setFormData({
      name: '',
      code: '',
      capacity: 30,
      type: 'CLASSROOM',
    });
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Rooms</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage rooms and facilities in the system
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add Room
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading rooms...</div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {rooms.length === 0 ? (
                <li className="px-4 py-8 text-center text-gray-500">
                  No rooms found. Click "Add Room" to create one.
                </li>
              ) : (
                rooms.map((room) => (
                  <li key={room.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <div className="text-lg font-medium text-blue-600">
                              {room.name}
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex sm:space-x-6">
                              <p className="flex items-center text-sm text-gray-500">
                                Code: {room.code}
                              </p>
                              <p className="flex items-center text-sm text-gray-500">
                                Capacity: {room.capacity}
                              </p>
                              <p className="flex items-center text-sm text-gray-500">
                                Type: {room.type}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="ml-4 flex-shrink-0 flex space-x-2">
                          <button
                            onClick={() => handleEdit(room)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(room.id)}
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
                {editingRoom ? 'Edit Room' : 'Add Room'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Room Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="e.g., Room 101"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Room Code
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.code}
                    onChange={(e) =>
                      setFormData({ ...formData, code: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="e.g., R101"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Capacity
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.capacity}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        capacity: parseInt(e.target.value),
                      })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Room Type
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) =>
                      setFormData({ ...formData, type: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  >
                    <option value="CLASSROOM">Classroom</option>
                    <option value="LAB">Laboratory</option>
                    <option value="AUDITORIUM">Auditorium</option>
                    <option value="LIBRARY">Library</option>
                    <option value="SPORTS">Sports Room</option>
                  </select>
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
                    {editingRoom ? 'Update' : 'Create'}
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