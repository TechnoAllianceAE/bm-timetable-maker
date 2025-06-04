'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import type { NavItem } from '@/types';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';


interface SidebarNavProps {
  items: NavItem[];
  onLinkClick?: () => void; // For mobile sidebar to close on click
}

export function SidebarNav({ items, onLinkClick }: SidebarNavProps) {
  const pathname = usePathname();

  if (!items.length) {
    return null;
  }
  
  const renderNavItem = (item: NavItem, isSubItem: boolean = false) => {
    const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
    const itemClass = cn(
      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
      isActive
        ? "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
        : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
      isSubItem ? "pl-8" : "" // Indent sub-items
    );

    return (
       <Link href={item.href} passHref legacyBehavior key={item.href}>
        <a onClick={onLinkClick} className={itemClass}>
          <item.icon className={cn("h-5 w-5 shrink-0", isActive ? "text-sidebar-primary-foreground" : "text-sidebar-foreground group-hover:text-sidebar-accent-foreground")} />
          <span className="truncate">{item.label}</span>
        </a>
      </Link>
    );
  }


  return (
    <ScrollArea className="flex-1">
      <nav className="grid items-start gap-1 p-2">
        {items.map((item) => 
          item.children && item.children.length > 0 ? (
            <Accordion type="single" collapsible key={item.label} className="w-full">
              <AccordionItem value={item.label} className="border-none">
                <AccordionTrigger 
                  className={cn(
                    "flex items-center justify-between gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground hover:no-underline",
                    pathname.startsWith(item.href) && item.href !== '/dashboard' ? "bg-sidebar-accent text-sidebar-accent-foreground" : ""
                  )}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="h-5 w-5 shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-0">
                  <div className="grid items-start gap-1 pl-4 mt-1">
                    {item.children.map((child) => renderNavItem(child, true))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          ) : (
            renderNavItem(item)
          )
        )}
      </nav>
    </ScrollArea>
  );
}
