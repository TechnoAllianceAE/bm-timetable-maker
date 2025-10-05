'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import AdminLayout from '@/components/AdminLayout';
import { timetableAPI, schoolAPI, academicYearAPI, subjectAPI, classAPI } from '@/lib/api';

interface School {
  id: string;
  name: string;
}

interface AcademicYear {
  id: string;
  year: string;
  startDate?: string;
  endDate?: string;
}

interface Subject {
  id: string;
  name: string;
  code: string;
}

interface Class {
  id: string;
  name: string;
  grade: number;
}

interface GradeSubjectRequirement {
  grade: number;
  subjectId: string;
  periodsPerWeek: number;
}

interface GenerationParams {
  schoolId: string;
  academicYearId: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  periodsPerDay: number;
  daysPerWeek: number;
  periodDuration: number;
  breakDuration: number;
  lunchDuration: number;
  constraints: {
    maxConsecutiveTeachingHours: number;
    minBreaksBetweenClasses: number;
    avoidBackToBackDifficultSubjects: boolean;
    preferMorningForDifficultSubjects: boolean;
    balanceTeacherWorkload: boolean;
  };
  hardRules: {
    noTeacherConflicts: boolean;
    noRoomConflicts: boolean;
    respectTeacherAvailability: boolean;
    subjectPeriodsPerWeek: boolean;
    maxPeriodsPerDayPerTeacher: boolean;
    roomCapacityConstraints: boolean;
    labRequirements: boolean;
    oneTeacherPerSubject: boolean;
    useHomeClassroom: boolean;
  };
  softRules: {
    minimizeTeacherGaps: boolean;
    balanceSubjectDistribution: boolean;
    avoidSinglePeriodGaps: boolean;
    preferConsecutiveSubjects: boolean;
    minimizeRoomChanges: boolean;
    preferredTimeSlots: boolean;
    teacherPreferences: boolean;
  };
}

export default function GenerateTimetablePage() {
  const router = useRouter();
  const [schools, setSchools] = useState<School[]>([]);
  const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [subjectRequirements, setSubjectRequirements] = useState<GradeSubjectRequirement[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [diagnostics, setDiagnostics] = useState<any>(null);

  const [params, setParams] = useState<GenerationParams>({
    schoolId: '',
    academicYearId: '',
    name: '',
    description: '',
    startDate: '',
    endDate: '',
    periodsPerDay: 8,
    daysPerWeek: 5,
    periodDuration: 45,
    breakDuration: 10,
    lunchDuration: 30,
    constraints: {
      maxConsecutiveTeachingHours: 3,
      minBreaksBetweenClasses: 1,
      avoidBackToBackDifficultSubjects: true,
      preferMorningForDifficultSubjects: true,
      balanceTeacherWorkload: true,
    },
    hardRules: {
      noTeacherConflicts: true,
      noRoomConflicts: true,
      respectTeacherAvailability: true,
      subjectPeriodsPerWeek: true,
      maxPeriodsPerDayPerTeacher: true,
      roomCapacityConstraints: true,
      labRequirements: true,
      oneTeacherPerSubject: true,
      useHomeClassroom: true,
    },
    softRules: {
      minimizeTeacherGaps: true,
      balanceSubjectDistribution: true,
      avoidSinglePeriodGaps: true,
      preferConsecutiveSubjects: false,
      minimizeRoomChanges: true,
      preferredTimeSlots: false,
      teacherPreferences: false,
    },
  });

  useEffect(() => {
    fetchSchools();
  }, []);

  useEffect(() => {
    if (params.schoolId) {
      fetchAcademicYears(params.schoolId);
      fetchSubjects(params.schoolId);
      fetchClasses(params.schoolId);
    }
  }, [params.schoolId]);

  const fetchSchools = async () => {
    setLoading(true);
    try {
      const response = await schoolAPI.list();
      const schoolsData = response.data.data || [];
      setSchools(schoolsData);
      if (schoolsData.length > 0) {
        setParams(prev => ({ ...prev, schoolId: schoolsData[0].id }));
      }
    } catch (error) {
      console.error('Failed to fetch schools:', error);
      setError('Failed to load schools');
    } finally {
      setLoading(false);
    }
  };

  const fetchAcademicYears = async (schoolId: string) => {
    try {
      // For now, use a mock academic year since the API endpoint doesn't exist yet
      // In the future, this should call: const response = await academicYearAPI.list(schoolId);
      const mockAcademicYears = [
        {
          id: 'cmg4x4ixh0001ouno5q5d9eb6', // Actual academic year ID from database
          year: '2024-2025',
          startDate: '2024-09-01',
          endDate: '2025-06-30'
        }
      ];
      setAcademicYears(mockAcademicYears);
      setParams(prev => ({ ...prev, academicYearId: mockAcademicYears[0].id }));
    } catch (error) {
      console.error('Failed to fetch academic years:', error);
      setError('Failed to load academic years');
    }
  };

  const fetchSubjects = async (schoolId: string) => {
    try {
      const response = await subjectAPI.list();
      const subjectsData = response.data.data || [];
      setSubjects(subjectsData);
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    }
  };

  const fetchClasses = async (schoolId: string) => {
    try {
      const response = await classAPI.list();
      const classesData = response.data.data || [];
      setClasses(classesData);
    } catch (error) {
      console.error('Failed to fetch classes:', error);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setError('');
    setGenerationResult(null);
    setDiagnostics(null);

    try {
      // Transform the form data to match the backend API structure
      const payload = {
        schoolId: params.schoolId,
        academicYearId: params.academicYearId,
        name: params.name,
        startDate: params.startDate,
        endDate: params.endDate,
        constraints: {
          // Basic constraints
          maxConsecutiveTeachingHours: params.constraints.maxConsecutiveTeachingHours,
          minBreaksBetweenClasses: params.constraints.minBreaksBetweenClasses,
          avoidBackToBackDifficultSubjects: params.constraints.avoidBackToBackDifficultSubjects,
          preferMorningForDifficultSubjects: params.constraints.preferMorningForDifficultSubjects,
          balanceTeacherWorkload: params.constraints.balanceTeacherWorkload,

          // Schedule structure
          periodsPerDay: params.periodsPerDay,
          daysPerWeek: params.daysPerWeek,
          periodDuration: params.periodDuration,
          breakDuration: params.breakDuration,
          lunchDuration: params.lunchDuration,

          // Hard rules
          hardRules: params.hardRules,

          // Soft rules
          softRules: params.softRules,
        },
        // Subject requirements (optional)
        subjectRequirements: subjectRequirements.length > 0 ? subjectRequirements : undefined
      };

      console.log('Sending timetable generation payload:', payload);
      console.log('Auth token available:', !!localStorage.getItem('token'));

      const response = await timetableAPI.generate(payload);
      setGenerationResult(response.data);

      // Extract diagnostics if available
      if (response.data.diagnostics) {
        setDiagnostics(response.data.diagnostics);
      }

      if (response.data.status === 'success') {
        setTimeout(() => {
          router.push('/admin/timetables');
        }, 3000);
      }
    } catch (err: any) {
      console.error('Timetable generation error:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      console.error('Error headers:', err.response?.headers);

      // Extract diagnostics from error response if available
      if (err.response?.data?.diagnostics) {
        setDiagnostics(err.response.data.diagnostics);
      }

      setError(err.response?.data?.message || err.message || 'Failed to generate timetable');
    } finally {
      setGenerating(false);
    }
  };

  const handleConstraintChange = (key: keyof typeof params.constraints, value: any) => {
    setParams(prev => ({
      ...prev,
      constraints: {
        ...prev.constraints,
        [key]: value,
      },
    }));
  };

  const handleHardRuleChange = (key: keyof typeof params.hardRules, value: boolean) => {
    setParams(prev => ({
      ...prev,
      hardRules: {
        ...prev.hardRules,
        [key]: value,
      },
    }));
  };

  const handleSoftRuleChange = (key: keyof typeof params.softRules, value: boolean) => {
    setParams(prev => ({
      ...prev,
      softRules: {
        ...prev.softRules,
        [key]: value,
      },
    }));
  };

  // Subject Requirements Management
  const addRequirement = () => {
    if (subjects.length === 0) {
      setError('Please wait for subjects to load');
      return;
    }

    // Get unique grades from classes
    const grades = Array.from(new Set(classes.map(c => c.grade))).sort((a, b) => a - b);
    const defaultGrade = grades[0] || 1;

    setSubjectRequirements([...subjectRequirements, {
      grade: defaultGrade,
      subjectId: subjects[0]?.id || '',
      periodsPerWeek: 5
    }]);
  };

  const updateRequirement = (index: number, field: keyof GradeSubjectRequirement, value: any) => {
    const updated = [...subjectRequirements];
    updated[index] = { ...updated[index], [field]: value };
    setSubjectRequirements(updated);
  };

  const removeRequirement = (index: number) => {
    setSubjectRequirements(subjectRequirements.filter((_, i) => i !== index));
  };

  // Get total required periods for a grade
  const getGradeTotalPeriods = (grade: number): number => {
    return subjectRequirements
      .filter(req => req.grade === grade)
      .reduce((sum, req) => sum + req.periodsPerWeek, 0);
  };

  // Get available periods per week
  const totalPeriodsPerWeek = params.periodsPerDay * params.daysPerWeek;

  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Generate Timetable</h1>
          <p className="mt-1 text-sm text-gray-600">
            Configure parameters and constraints for automatic timetable generation
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-500">Loading...</div>
          </div>
        ) : (
          <form onSubmit={handleGenerate} className="space-y-6 bg-white shadow rounded-lg p-6">
            {/* Basic Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    School
                  </label>
                  <select
                    required
                    value={params.schoolId}
                    onChange={(e) => setParams({ ...params, schoolId: e.target.value, academicYearId: '' })}
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
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Academic Year
                  </label>
                  <select
                    required
                    value={params.academicYearId}
                    onChange={(e) => setParams({ ...params, academicYearId: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    disabled={!params.schoolId}
                  >
                    <option value="">Select an academic year</option>
                    {academicYears.map((year) => (
                      <option key={year.id} value={year.id}>
                        {year.year}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Timetable Name
                  </label>
                  <input
                    type="text"
                    required
                    value={params.name}
                    onChange={(e) => setParams({ ...params, name: e.target.value })}
                    placeholder="e.g., Spring Semester 2024"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    value={params.description}
                    onChange={(e) => setParams({ ...params, description: e.target.value })}
                    rows={2}
                    placeholder="Optional description..."
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Start Date
                  </label>
                  <input
                    type="date"
                    required
                    value={params.startDate}
                    onChange={(e) => setParams({ ...params, startDate: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    End Date
                  </label>
                  <input
                    type="date"
                    required
                    value={params.endDate}
                    onChange={(e) => setParams({ ...params, endDate: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
              </div>
            </div>

            {/* Schedule Structure */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Schedule Structure</h2>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Periods Per Day
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="12"
                    required
                    value={params.periodsPerDay}
                    onChange={(e) =>
                      setParams({ ...params, periodsPerDay: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Days Per Week
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="7"
                    required
                    value={params.daysPerWeek}
                    onChange={(e) =>
                      setParams({ ...params, daysPerWeek: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Period Duration (min)
                  </label>
                  <input
                    type="number"
                    min="15"
                    max="90"
                    required
                    value={params.periodDuration}
                    onChange={(e) =>
                      setParams({ ...params, periodDuration: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Break Duration (min)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="30"
                    required
                    value={params.breakDuration}
                    onChange={(e) =>
                      setParams({ ...params, breakDuration: parseInt(e.target.value) })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
              </div>
            </div>

            {/* Constraints */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Constraints & Preferences</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Max Consecutive Teaching Hours
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="6"
                      value={params.constraints.maxConsecutiveTeachingHours}
                      onChange={(e) =>
                        handleConstraintChange(
                          'maxConsecutiveTeachingHours',
                          parseInt(e.target.value)
                        )
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Min Breaks Between Classes
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="3"
                      value={params.constraints.minBreaksBetweenClasses}
                      onChange={(e) =>
                        handleConstraintChange(
                          'minBreaksBetweenClasses',
                          parseInt(e.target.value)
                        )
                      }
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.avoidBackToBackDifficultSubjects}
                      onChange={(e) =>
                        handleConstraintChange(
                          'avoidBackToBackDifficultSubjects',
                          e.target.checked
                        )
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Avoid back-to-back difficult subjects
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.preferMorningForDifficultSubjects}
                      onChange={(e) =>
                        handleConstraintChange(
                          'preferMorningForDifficultSubjects',
                          e.target.checked
                        )
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Schedule difficult subjects in morning periods
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={params.constraints.balanceTeacherWorkload}
                      onChange={(e) =>
                        handleConstraintChange('balanceTeacherWorkload', e.target.checked)
                      }
                      className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Balance teacher workload across days
                    </span>
                  </label>
                </div>
              </div>
            </div>

            {/* Hard Rules */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Hard Rules
                <span className="text-sm text-red-600 ml-2">(Must be satisfied)</span>
              </h2>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.noTeacherConflicts}
                    onChange={(e) => handleHardRuleChange('noTeacherConflicts', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    No teacher conflicts - A teacher cannot be in two places at once
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.noRoomConflicts}
                    onChange={(e) => handleHardRuleChange('noRoomConflicts', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    No room conflicts - A room cannot host multiple classes simultaneously
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.respectTeacherAvailability}
                    onChange={(e) => handleHardRuleChange('respectTeacherAvailability', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Respect teacher availability - Only assign teachers when they are available
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.subjectPeriodsPerWeek}
                    onChange={(e) => handleHardRuleChange('subjectPeriodsPerWeek', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Meet subject period requirements - Ensure minimum periods per week for each subject
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.maxPeriodsPerDayPerTeacher}
                    onChange={(e) => handleHardRuleChange('maxPeriodsPerDayPerTeacher', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Respect teacher daily limits - Don't exceed maximum periods per day per teacher
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.roomCapacityConstraints}
                    onChange={(e) => handleHardRuleChange('roomCapacityConstraints', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Room capacity constraints - Ensure class size doesn't exceed room capacity
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.labRequirements}
                    onChange={(e) => handleHardRuleChange('labRequirements', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Lab requirements - Assign lab subjects to appropriate lab rooms
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.oneTeacherPerSubject}
                    onChange={(e) => handleHardRuleChange('oneTeacherPerSubject', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    One teacher per subject per class - Same teacher teaches all periods of a subject to the same class
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.hardRules.useHomeClassroom}
                    onChange={(e) => handleHardRuleChange('useHomeClassroom', e.target.checked)}
                    className="rounded border-gray-300 text-red-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Use home classrooms - Regular subjects use dedicated home classroom, labs remain shared
                  </span>
                </label>
              </div>
            </div>

            {/* Soft Rules */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Soft Rules
                <span className="text-sm text-blue-600 ml-2">(Preferred but flexible)</span>
              </h2>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.minimizeTeacherGaps}
                    onChange={(e) => handleSoftRuleChange('minimizeTeacherGaps', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Minimize teacher gaps - Reduce free periods between classes for teachers
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.balanceSubjectDistribution}
                    onChange={(e) => handleSoftRuleChange('balanceSubjectDistribution', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Balance subject distribution - Spread subjects evenly across days
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.avoidSinglePeriodGaps}
                    onChange={(e) => handleSoftRuleChange('avoidSinglePeriodGaps', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Avoid single period gaps - Prevent isolated free periods in schedules
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.preferConsecutiveSubjects}
                    onChange={(e) => handleSoftRuleChange('preferConsecutiveSubjects', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Prefer consecutive subjects - Group multiple periods of same subject together
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.minimizeRoomChanges}
                    onChange={(e) => handleSoftRuleChange('minimizeRoomChanges', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Minimize room changes - Keep classes in same room when possible
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.preferredTimeSlots}
                    onChange={(e) => handleSoftRuleChange('preferredTimeSlots', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Respect preferred time slots - Consider teacher and subject time preferences
                  </span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={params.softRules.teacherPreferences}
                    onChange={(e) => handleSoftRuleChange('teacherPreferences', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 shadow-sm mr-3"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Teacher preferences - Consider individual teacher scheduling preferences
                  </span>
                </label>
              </div>
            </div>

            {/* Subject Hour Requirements */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">
                Subject Hour Requirements
                <span className="text-sm text-gray-600 ml-2">(Optional)</span>
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Specify required periods per week for each subject in each grade. If not specified, default values from subject configuration will be used.
              </p>

              {subjectRequirements.length > 0 && (
                <div className="mb-4 overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Grade</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Subject</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Periods/Week</th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {subjectRequirements.map((req, index) => {
                        const gradeTotal = getGradeTotalPeriods(req.grade);
                        const isOverLimit = gradeTotal > totalPeriodsPerWeek;

                        return (
                          <tr key={index} className={isOverLimit ? 'bg-red-50' : ''}>
                            <td className="px-4 py-3">
                              <select
                                value={req.grade}
                                onChange={(e) => updateRequirement(index, 'grade', parseInt(e.target.value))}
                                className="border border-gray-300 rounded px-2 py-1 text-sm"
                              >
                                {Array.from(new Set(classes.map(c => c.grade))).sort((a, b) => a - b).map(g => (
                                  <option key={g} value={g}>Grade {g}</option>
                                ))}
                              </select>
                            </td>
                            <td className="px-4 py-3">
                              <select
                                value={req.subjectId}
                                onChange={(e) => updateRequirement(index, 'subjectId', e.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 text-sm w-full"
                              >
                                {subjects.map(s => (
                                  <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                              </select>
                            </td>
                            <td className="px-4 py-3">
                              <input
                                type="number"
                                min="1"
                                max="40"
                                value={req.periodsPerWeek}
                                onChange={(e) => updateRequirement(index, 'periodsPerWeek', parseInt(e.target.value) || 1)}
                                className="border border-gray-300 rounded px-2 py-1 text-sm w-20"
                              />
                            </td>
                            <td className="px-4 py-3 text-right">
                              <button
                                onClick={() => removeRequirement(index)}
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              <button
                onClick={addRequirement}
                disabled={subjects.length === 0 || classes.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm font-medium"
              >
                + Add Requirement
              </button>

              {/* Grade totals summary */}
              {subjectRequirements.length > 0 && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">Total Periods per Grade</h4>
                  <div className="space-y-1">
                    {Array.from(new Set(subjectRequirements.map(r => r.grade))).sort((a, b) => a - b).map(grade => {
                      const total = getGradeTotalPeriods(grade);
                      const isOverLimit = total > totalPeriodsPerWeek;
                      return (
                        <div key={grade} className={`text-sm ${isOverLimit ? 'text-red-700 font-bold' : 'text-blue-700'}`}>
                          Grade {grade}: {total}/{totalPeriodsPerWeek} periods
                          {isOverLimit && <span className="ml-2 text-red-600">(Exceeds limit!)</span>}
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-xs text-blue-600 mt-2">
                    Available periods per week: {params.periodsPerDay} periods/day × {params.daysPerWeek} days = {totalPeriodsPerWeek} periods
                  </p>
                </div>
              )}
            </div>

            {/* Error Display with Diagnostics */}
            {error && (
              <div className="rounded-md bg-red-50 p-4 space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <span className="text-red-400 text-lg">❌</span>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Generation Failed</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>

                {/* Diagnostic Information */}
                {diagnostics && (
                  <div className="border-t border-red-200 pt-4">
                    <h4 className="text-sm font-medium text-red-800 mb-3">🔍 Diagnostic Analysis</h4>

                    {/* Critical Issues */}
                    {diagnostics.critical_issues && diagnostics.critical_issues.length > 0 && (
                      <div className="mb-4">
                        <h5 className="text-xs font-medium text-red-800 mb-2 uppercase tracking-wide">Critical Issues</h5>
                        <div className="space-y-2">
                          {diagnostics.critical_issues.map((issue: any, index: number) => (
                            <div key={index} className="bg-red-100 rounded p-3">
                              <div className="flex items-center mb-1">
                                <span className="text-red-600 text-xs font-medium uppercase">{issue.type}</span>
                              </div>
                              <p className="text-sm text-red-700 mb-2">{issue.message}</p>
                              {issue.suggestions && issue.suggestions.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-xs font-medium text-red-600 mb-1">Suggested Solutions:</p>
                                  <ul className="text-xs text-red-600 space-y-1">
                                    {issue.suggestions.map((suggestion: string, idx: number) => (
                                      <li key={idx} className="flex items-start">
                                        <span className="mr-1">•</span>
                                        <span>{suggestion}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Resource Bottlenecks */}
                    {diagnostics.bottleneck_resources && Object.keys(diagnostics.bottleneck_resources).length > 0 && (
                      <div className="mb-4">
                        <h5 className="text-xs font-medium text-red-800 mb-2 uppercase tracking-wide">Resource Bottlenecks</h5>
                        <div className="space-y-1">
                          {Object.entries(diagnostics.bottleneck_resources).map(([resource, score]: [string, any]) => (
                            <div key={resource} className="flex items-center justify-between bg-red-100 rounded px-3 py-2">
                              <span className="text-xs font-medium text-red-700 capitalize">{resource.replace('_', ' ')}</span>
                              <div className="flex items-center space-x-2">
                                <div className="w-16 bg-red-200 rounded-full h-2">
                                  <div
                                    className="bg-red-600 h-2 rounded-full"
                                    style={{ width: `${Math.min(100, score)}%` }}
                                  ></div>
                                </div>
                                <span className="text-xs text-red-600 font-medium">{Math.round(score)}%</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {diagnostics.recommendations && diagnostics.recommendations.length > 0 && (
                      <div>
                        <h5 className="text-xs font-medium text-red-800 mb-2 uppercase tracking-wide">💡 Recommendations</h5>
                        <div className="bg-red-100 rounded p-3">
                          <ul className="text-xs text-red-700 space-y-1">
                            {diagnostics.recommendations.map((rec: string, index: number) => (
                              <li key={index} className="flex items-start">
                                <span className="mr-1 text-red-500">▶</span>
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Generation Result with Enhanced Diagnostics */}
            {generationResult && (
              <div
                className={`rounded-md p-4 space-y-4 ${
                  generationResult.status === 'success'
                    ? 'bg-green-50'
                    : generationResult.status === 'partial'
                    ? 'bg-yellow-50'
                    : generationResult.status === 'infeasible'
                    ? 'bg-orange-50'
                    : 'bg-red-50'
                }`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <span className="text-lg">
                      {generationResult.status === 'success'
                        ? '✅'
                        : generationResult.status === 'partial'
                        ? '⚠️'
                        : generationResult.status === 'infeasible'
                        ? '🚫'
                        : '❌'}
                    </span>
                  </div>
                  <div className="ml-3 flex-1">
                    <h3
                      className={`text-sm font-medium mb-2 ${
                        generationResult.status === 'success'
                          ? 'text-green-800'
                          : generationResult.status === 'partial'
                          ? 'text-yellow-800'
                          : generationResult.status === 'infeasible'
                          ? 'text-orange-800'
                          : 'text-red-800'
                      }`}
                    >
                      {generationResult.status === 'success'
                        ? 'Timetable Generated Successfully!'
                        : generationResult.status === 'partial'
                        ? 'Partial Timetable Generated'
                        : generationResult.status === 'infeasible'
                        ? 'Problem is Mathematically Infeasible'
                        : 'Generation Failed'}
                    </h3>

                    {/* Generation Statistics */}
                    {generationResult.generation_time && (
                      <div className="flex items-center space-x-4 text-xs text-gray-600 mb-3">
                        <span>⏱️ Generated in {generationResult.generation_time}s</span>
                        {generationResult.solutions && (
                          <span>📊 {generationResult.solutions.length} solution(s) found</span>
                        )}
                      </div>
                    )}

                    {generationResult.message && (
                      <p
                        className={`text-sm mb-3 ${
                          generationResult.status === 'success'
                            ? 'text-green-700'
                            : generationResult.status === 'partial'
                            ? 'text-yellow-700'
                            : generationResult.status === 'infeasible'
                            ? 'text-orange-700'
                            : 'text-red-700'
                        }`}
                      >
                        {generationResult.message}
                      </p>
                    )}

                    {/* Success Diagnostics */}
                    {generationResult.status === 'success' && generationResult.diagnostics && (
                      <div className="border-t border-green-200 pt-4">
                        <h4 className="text-sm font-medium text-green-800 mb-3">📊 Generation Analytics</h4>

                        {/* Optimization Summary */}
                        {generationResult.diagnostics.optimization_summary && (
                          <div className="bg-green-100 rounded p-3 mb-3">
                            <h5 className="text-xs font-medium text-green-800 mb-2 uppercase tracking-wide">Optimization Performance</h5>
                            <div className="grid grid-cols-3 gap-4 text-xs">
                              {generationResult.diagnostics.optimization_summary.csp_time && (
                                <div className="text-center">
                                  <div className="text-green-600 font-medium">⚡ CSP Solver</div>
                                  <div className="text-green-700">{generationResult.diagnostics.optimization_summary.csp_time}s</div>
                                </div>
                              )}
                              {generationResult.diagnostics.optimization_summary.total_iterations && (
                                <div className="text-center">
                                  <div className="text-green-600 font-medium">🔄 Iterations</div>
                                  <div className="text-green-700">{generationResult.diagnostics.optimization_summary.total_iterations}</div>
                                </div>
                              )}
                              {generationResult.diagnostics.optimization_summary.final_fitness && (
                                <div className="text-center">
                                  <div className="text-green-600 font-medium">🎯 Quality Score</div>
                                  <div className="text-green-700">{Math.round(generationResult.diagnostics.optimization_summary.final_fitness)}%</div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Resource Utilization */}
                        {generationResult.diagnostics.resource_utilization && Object.keys(generationResult.diagnostics.resource_utilization).length > 0 && (
                          <div className="bg-green-100 rounded p-3 mb-3">
                            <h5 className="text-xs font-medium text-green-800 mb-2 uppercase tracking-wide">Resource Utilization</h5>
                            <div className="space-y-1">
                              {Object.entries(generationResult.diagnostics.resource_utilization).map(([resource, utilization]: [string, any]) => (
                                <div key={resource} className="flex items-center justify-between">
                                  <span className="text-xs font-medium text-green-700 capitalize">{resource.replace('_', ' ')}</span>
                                  <div className="flex items-center space-x-2">
                                    <div className="w-16 bg-green-200 rounded-full h-2">
                                      <div
                                        className="bg-green-600 h-2 rounded-full"
                                        style={{ width: `${Math.min(100, utilization)}%` }}
                                      ></div>
                                    </div>
                                    <span className="text-xs text-green-600 font-medium">{Math.round(utilization)}%</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Warnings (if any) - Check both top-level and diagnostics */}
                        {((generationResult.warnings && generationResult.warnings.length > 0) ||
                          (generationResult.diagnostics?.warnings && generationResult.diagnostics.warnings.length > 0)) && (
                          <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
                            <h5 className="text-xs font-medium text-yellow-800 mb-2 uppercase tracking-wide">⚠️ Validation Warnings</h5>
                            <ul className="text-xs text-yellow-700 space-y-1">
                              {/* Display top-level warnings first */}
                              {generationResult.warnings && generationResult.warnings.map((warning: string, index: number) => (
                                <li key={`w-${index}`} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span>{warning}</span>
                                </li>
                              ))}
                              {/* Display diagnostics warnings */}
                              {generationResult.diagnostics?.warnings && generationResult.diagnostics.warnings.map((warning: string, index: number) => (
                                <li key={`d-${index}`} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span>{warning}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Informational Messages (if any) */}
                        {generationResult.info && generationResult.info.length > 0 && (
                          <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
                            <h5 className="text-xs font-medium text-blue-800 mb-2 uppercase tracking-wide">ℹ️ Information</h5>
                            <ul className="text-xs text-blue-700 space-y-1">
                              {generationResult.info.map((info: string, index: number) => (
                                <li key={index} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span>{info}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Convergence Analysis */}
                        {generationResult.diagnostics.convergence && (
                          <div className="bg-green-100 rounded p-3">
                            <h5 className="text-xs font-medium text-green-800 mb-1 uppercase tracking-wide">Algorithm Status</h5>
                            <p className="text-xs text-green-700">{generationResult.diagnostics.convergence}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Failed/Infeasible Diagnostics */}
                    {(generationResult.status === 'failed' || generationResult.status === 'infeasible') && generationResult.diagnostics && (
                      <div className={`border-t pt-4 ${generationResult.status === 'infeasible' ? 'border-orange-200' : 'border-red-200'}`}>
                        <h4 className={`text-sm font-medium mb-3 ${generationResult.status === 'infeasible' ? 'text-orange-800' : 'text-red-800'}`}>
                          🔍 Failure Analysis
                        </h4>

                        {/* Solver Stage */}
                        {generationResult.diagnostics.solver_stage && (
                          <div className={`rounded p-3 mb-3 ${generationResult.status === 'infeasible' ? 'bg-orange-100' : 'bg-red-100'}`}>
                            <p className={`text-xs ${generationResult.status === 'infeasible' ? 'text-orange-700' : 'text-red-700'}`}>
                              Failed at: <span className="font-medium">{generationResult.diagnostics.solver_stage} stage</span>
                            </p>
                          </div>
                        )}

                        {/* Conflicts - Check both top-level and diagnostics */}
                        {((generationResult.conflicts && generationResult.conflicts.length > 0) ||
                          (generationResult.diagnostics?.conflicts && generationResult.diagnostics.conflicts.length > 0)) && (
                          <div className={`rounded p-3 mb-3 ${generationResult.status === 'infeasible' ? 'bg-orange-100' : 'bg-red-100'}`}>
                            <h5 className={`text-xs font-medium mb-2 uppercase tracking-wide ${generationResult.status === 'infeasible' ? 'text-orange-800' : 'text-red-800'}`}>
                              Detected Conflicts
                            </h5>
                            <ul className={`text-xs space-y-1 ${generationResult.status === 'infeasible' ? 'text-orange-700' : 'text-red-700'}`}>
                              {generationResult.conflicts && generationResult.conflicts.map((conflict: string, index: number) => (
                                <li key={`c-${index}`} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span className="capitalize">{conflict.replace('_', ' ')}</span>
                                </li>
                              ))}
                              {generationResult.diagnostics?.conflicts && generationResult.diagnostics.conflicts.map((conflict: string, index: number) => (
                                <li key={`dc-${index}`} className="flex items-start">
                                  <span className="mr-1">•</span>
                                  <span className="capitalize">{conflict.replace('_', ' ')}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Suggestions - Check both top-level and diagnostics */}
                        {((generationResult.suggestions && generationResult.suggestions.length > 0) ||
                          (generationResult.diagnostics?.suggestions && generationResult.diagnostics.suggestions.length > 0)) && (
                          <div className={`rounded p-3 ${generationResult.status === 'infeasible' ? 'bg-orange-100' : 'bg-red-100'}`}>
                            <h5 className={`text-xs font-medium mb-2 uppercase tracking-wide ${generationResult.status === 'infeasible' ? 'text-orange-800' : 'text-red-800'}`}>
                              💡 Suggested Actions
                            </h5>
                            <ul className={`text-xs space-y-1 ${generationResult.status === 'infeasible' ? 'text-orange-700' : 'text-red-700'}`}>
                              {generationResult.suggestions && generationResult.suggestions.map((suggestion: string, index: number) => (
                                <li key={`s-${index}`} className="flex items-start">
                                  <span className="mr-1">▶</span>
                                  <span>{suggestion}</span>
                                </li>
                              ))}
                              {generationResult.diagnostics?.suggestions && generationResult.diagnostics.suggestions.map((suggestion: string, index: number) => (
                                <li key={`ds-${index}`} className="flex items-start">
                                  <span className="mr-1">▶</span>
                                  <span>{suggestion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {generationResult.status === 'success' && (
                      <div className="mt-4 flex items-center justify-between bg-green-100 rounded p-3">
                        <p className="text-sm text-green-600">
                          ✨ Timetable ready! Redirecting to view...
                        </p>
                        <div className="text-xs text-green-500">
                          Auto-redirect in 3s
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => router.push('/admin/timetables')}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={generating || !params.schoolId || !params.academicYearId}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⚙️</span>
                    Generating...
                  </>
                ) : (
                  'Generate Timetable'
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </AdminLayout>
  );
}