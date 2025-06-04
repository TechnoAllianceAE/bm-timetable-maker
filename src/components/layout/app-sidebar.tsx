'use client';

import { useAuth } from '@/hooks/use-auth';
import { filterNavItemsByRole, filterBottomNavItemsByRole } from '@/constants/navigation';
import { SidebarNav } from './sidebar-nav';
import { Logo } from '../icons';
import { Separator } from '../ui/separator';

export function AppSidebar() {
  const { user } = useAuth();

  if (!user) {
    return null; // Or some loading state
  }

  const currentNavItems = filterNavItemsByRole(user.role);
  const currentBottomNavItems = filterBottomNavItemsByRole(user.role);

  return (
    <div className="hidden border-r bg-sidebar md:block text-sidebar-foreground">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-16 items-center border-b border-sidebar-border px-4">
          <Logo className="h-8 w-auto text-sidebar-foreground" />
        </div>
        <SidebarNav items={currentNavItems} />
        {currentBottomNavItems.length > 0 && (
          <>
            <div className="mt-auto p-2">
               <Separator className="my-2 bg-sidebar-border"/>
              <SidebarNav items={currentBottomNavItems} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
