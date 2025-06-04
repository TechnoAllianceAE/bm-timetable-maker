'use client';

import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useAuth } from '@/hooks/use-auth';
import { filterNavItemsByRole, filterBottomNavItemsByRole, navItems, bottomNavItems } from '@/constants/navigation';
import { SidebarNav } from './sidebar-nav';
import { Logo } from '../icons';
import { UserAvatar } from './user-avatar';
import { useIsMobile } from '@/hooks/use-mobile'; // Assuming this hook exists
import { useState } from 'react';

export function Header() {
  const { user } = useAuth();
  const isMobile = useIsMobile();
  const [mobileSheetOpen, setMobileSheetOpen] = useState(false);

  const currentNavItems = user ? filterNavItemsByRole(user.role) : [];
  const currentBottomNavItems = user ? filterBottomNavItemsByRole(user.role) : [];

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-card px-4 md:px-6 shadow-sm">
      {isMobile && (
        <Sheet open={mobileSheetOpen} onOpenChange={setMobileSheetOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="shrink-0 md:hidden">
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="flex flex-col p-0 bg-sidebar text-sidebar-foreground w-3/4 max-w-xs">
            <div className="flex h-16 items-center border-b border-sidebar-border px-4">
              <Logo className="h-8 w-auto text-sidebar-foreground" />
            </div>
            <SidebarNav items={currentNavItems} onLinkClick={() => setMobileSheetOpen(false)} />
            {currentBottomNavItems.length > 0 && (
              <>
                <div className="mt-auto border-t border-sidebar-border p-2">
                  <SidebarNav items={currentBottomNavItems} onLinkClick={() => setMobileSheetOpen(false)} />
                </div>
              </>
            )}
          </SheetContent>
        </Sheet>
      )}
      <div className="flex-1">
        {/* Breadcrumbs or page title can go here */}
      </div>
      <UserAvatar />
    </header>
  );
}
