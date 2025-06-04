'use client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { ArrowRight, BarChart3, ClipboardEdit, FilePlus2, AlertTriangle, Settings } from "lucide-react";
import Link from "next/link";

const QuickAction = ({ title, description, href, icon: Icon }: { title: string, description: string, href: string, icon: React.ElementType }) => (
  <Card className="hover:shadow-lg transition-shadow">
    <CardHeader className="flex flex-row items-center justify-between pb-2">
      <CardTitle className="text-lg font-medium font-headline">{title}</CardTitle>
      <Icon className="h-6 w-6 text-accent" />
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground mb-4">{description}</p>
      <Button variant="outline" asChild className="border-primary text-primary hover:bg-primary/10 hover:text-primary">
        <Link href={href}>
          Go to {title} <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </CardContent>
  </Card>
);

export default function DashboardPage() {
  const { user } = useAuth();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  }

  return (
    <div className="space-y-6">
      <div className="pb-2 border-b">
        <h1 className="text-3xl font-headline tracking-tight">{getGreeting()}, {user?.name || 'User'}!</h1>
        <p className="text-muted-foreground">Welcome to your K12 Timetable Ace dashboard.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {user?.role === 'Timetable Coordinator' || user?.role === 'School Admin' ? (
          <>
            <QuickAction 
              title="Generate Timetable" 
              description="Use AI to create a new school timetable." 
              href="/dashboard/timetable-generation"
              icon={FilePlus2}
            />
            <QuickAction 
              title="Manual Editor" 
              description="View and manually adjust existing timetables." 
              href="/dashboard/manual-editor"
              icon={ClipboardEdit}
            />
            <QuickAction 
              title="Disruption Solver" 
              description="Quickly find solutions for timetable disruptions." 
              href="/dashboard/disruption-solver"
              icon={AlertTriangle}
            />
          </>
        ) : null}

        {user?.role === 'School Admin' ? (
           <QuickAction 
              title="School Setup" 
              description="Manage teachers, classrooms, subjects, and constraints." 
              href="/dashboard/school-setup"
              icon={Settings}
            />
        ): null}
        
        {user?.role === 'Teacher' ? (
           <>
            <QuickAction 
              title="My Schedule" 
              description="View your personal teaching schedule." 
              href="/dashboard/my-schedule"
              icon={ClipboardEdit}
            />
             <QuickAction 
              title="Report Absence" 
              description="Notify administration about an upcoming absence." 
              href="/dashboard/report-absence"
              icon={AlertTriangle}
            />
          </>
        ): null}

         {user?.role === 'Super Admin' ? (
           <QuickAction 
              title="Global Settings" 
              description="Manage system-wide configurations and schools." 
              href="/dashboard/global-settings"
              icon={Settings}
            />
        ): null}

        <QuickAction 
          title="Analytics & Reports" 
          description="View resource utilization and compliance reports." 
          href="/dashboard/analytics"
          icon={BarChart3}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline">System Status</CardTitle>
          <CardDescription>Overview of current system health and notifications.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">System is operating normally. No critical alerts.</p>
          {/* More detailed status items can be added here */}
        </CardContent>
      </Card>
    </div>
  );
}
