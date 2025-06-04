import type { NavItem, UserRole } from '@/types';
import {
  LayoutDashboard,
  Users,
  Settings,
  CalendarDays,
  AlertTriangle,
  FileText,
  BookOpen,
  ClipboardEdit,
  BarChart3,
  LogOut,
  SlidersHorizontal,
  CalendarCheck,
  BellOff,
  FilePlus2
} from 'lucide-react';

export const ALL_ROLES: UserRole[] = ['Super Admin', 'School Admin', 'Timetable Coordinator', 'Teacher'];

export const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    allowedRoles: ALL_ROLES,
  },
  // Super Admin Specific
  {
    label: 'Global Settings',
    href: '/dashboard/global-settings',
    icon: Settings,
    allowedRoles: ['Super Admin'],
  },
  {
    label: 'Manage Schools',
    href: '/dashboard/manage-schools',
    icon: Users, // Placeholder, could be Building icon
    allowedRoles: ['Super Admin'],
  },
  // School Admin Specific
  {
    label: 'School Setup',
    href: '/dashboard/school-setup',
    icon: SlidersHorizontal,
    allowedRoles: ['School Admin'],
    children: [
       { label: 'Teachers', href: '/dashboard/school-setup/teachers', icon: Users, allowedRoles: ['School Admin'] },
       { label: 'Classrooms', href: '/dashboard/school-setup/classrooms', icon: BookOpen, allowedRoles: ['School Admin'] },
       { label: 'Subjects', href: '/dashboard/school-setup/subjects', icon: FileText, allowedRoles: ['School Admin'] },
       { label: 'Classes', href: '/dashboard/school-setup/classes', icon: Users, allowedRoles: ['School Admin'] },
       { label: 'Constraints', href: '/dashboard/school-setup/constraints', icon: AlertTriangle, allowedRoles: ['School Admin'] },
    ]
  },
  // Timetable Coordinator Specific
  {
    label: 'Timetable Generation',
    href: '/dashboard/timetable-generation',
    icon: FilePlus2,
    allowedRoles: ['Timetable Coordinator', 'School Admin'],
  },
  {
    label: 'Manual Editor',
    href: '/dashboard/manual-editor',
    icon: ClipboardEdit,
    allowedRoles: ['Timetable Coordinator', 'School Admin'],
  },
  {
    label: 'Disruption Solver',
    href: '/dashboard/disruption-solver',
    icon: AlertTriangle,
    allowedRoles: ['Timetable Coordinator', 'School Admin'],
  },
  // Teacher Specific
  {
    label: 'My Schedule',
    href: '/dashboard/my-schedule',
    icon: CalendarCheck,
    allowedRoles: ['Teacher'],
  },
  {
    label: 'Report Absence',
    href: '/dashboard/report-absence',
    icon: BellOff,
    allowedRoles: ['Teacher'],
  },
  {
    label: 'My Preferences',
    href: '/dashboard/preferences',
    icon: Settings, // UserCog might be better if available
    allowedRoles: ['Teacher'],
  },
  // Common for School Admin & Timetable Coordinator
  {
    label: 'Analytics & Reports',
    href: '/dashboard/analytics',
    icon: BarChart3,
    allowedRoles: ['School Admin', 'Timetable Coordinator', 'Super Admin'],
  },
  {
    label: 'User Management',
    href: '/dashboard/user-management',
    icon: Users,
    allowedRoles: ['School Admin', 'Super Admin'],
  }
];

export const bottomNavItems: NavItem[] = [
    {
    label: 'Account Settings',
    href: '/dashboard/account-settings',
    icon: Settings,
    allowedRoles: ALL_ROLES,
  },
];

export const filterNavItemsByRole = (role: UserRole): NavItem[] => {
  if (!role) return [];
  return navItems
    .map(item => {
      if (item.allowedRoles.includes(role)) {
        if (item.children) {
          const filteredChildren = item.children.filter(child => child.allowedRoles.includes(role));
          if (filteredChildren.length > 0) {
            return { ...item, children: filteredChildren };
          }
          // if no children are allowed, but parent is, show parent without children (if it's a direct link)
          // or hide parent if it only serves as a grouper for now-empty children
          return { ...item, children: undefined }; 
        }
        return item;
      }
      return null;
    })
    .filter(Boolean) as NavItem[];
};


export const filterBottomNavItemsByRole = (role: UserRole): NavItem[] => {
  if (!role) return [];
  return bottomNavItems.filter(item => item.allowedRoles.includes(role));
};
