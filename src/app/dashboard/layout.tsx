'use client';

import { useEffect } } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { AppSidebar } from '@/components/layout/app-sidebar';
import { Header } from '@/components/layout/header';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="grid md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr] w-full h-full">
          <div className="hidden border-r bg-muted/40 md:block">
            <div className="flex h-full max-h-screen flex-col gap-2 p-4">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-8 w-full mt-4" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full mt-auto" />
            </div>
          </div>
          <div className="flex flex-col">
            <header className="flex h-16 items-center gap-4 border-b bg-muted/40 px-4 lg:px-6">
              <Skeleton className="h-8 w-8 rounded-full md:hidden" />
              <div className="w-full flex-1">
                 <Skeleton className="h-8 w-1/3" />
              </div>
              <Skeleton className="h-10 w-10 rounded-full" />
            </header>
            <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
              <Skeleton className="h-12 w-1/2" />
              <Skeleton className="flex-1 w-full rounded-lg" />
            </main>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
      <AppSidebar />
      <div className="flex flex-col">
        <Header />
        <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6 bg-background overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
