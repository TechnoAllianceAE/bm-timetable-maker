export type UserRole = 'Super Admin' | 'School Admin' | 'Timetable Coordinator' | 'Teacher' | null;

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  schoolId?: string; // Optional, relevant for non-Super Admins
}

export interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  allowedRoles: UserRole[];
  children?: NavItem[];
}
