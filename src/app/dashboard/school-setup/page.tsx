'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users, BookOpen, FileText, AlertTriangle, ArrowRight } from "lucide-react";
import Link from "next/link";

const SetupItemCard = ({ title, description, href, icon: Icon }: { title: string, description: string, href: string, icon: React.ElementType }) => (
  <Card className="hover:shadow-lg transition-shadow">
    <CardHeader className="pb-4">
      <div className="flex items-center gap-3 mb-2">
        <Icon className="h-8 w-8 text-primary" />
        <CardTitle className="font-headline text-xl">{title}</CardTitle>
      </div>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
    <CardContent>
      <Button variant="outline" asChild className="w-full border-accent text-accent hover:bg-accent/10 hover:text-accent">
        <Link href={href}>
          Manage {title} <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </CardContent>
  </Card>
);


export default function SchoolSetupPage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">School Setup</CardTitle>
          <CardDescription>
            Configure essential data for your school, including teachers, classrooms, subjects, and operational constraints.
            This information is crucial for AI timetable generation.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SetupItemCard 
          title="Teachers" 
          description="Manage teacher profiles, subject expertise, and availability." 
          href="/dashboard/school-setup/teachers"
          icon={Users}
        />
        <SetupItemCard 
          title="Classrooms & Venues" 
          description="Define classrooms, labs, and other venues with their capacities and features." 
          href="/dashboard/school-setup/classrooms"
          icon={BookOpen} // Using BookOpen as a placeholder for classroom/venue
        />
        <SetupItemCard 
          title="Subjects & Courses" 
          description="List all subjects taught and define courses offered at different grade levels." 
          href="/dashboard/school-setup/subjects"
          icon={FileText}
        />
         <SetupItemCard 
          title="Classes & Sections" 
          description="Manage classes, sections, and student groups for timetable allocation." 
          href="/dashboard/school-setup/classes"
          icon={Users} // Placeholder icon
        />
        <SetupItemCard 
          title="Constraints & Rules" 
          description="Set school-specific hard and soft constraints for timetable optimization." 
          href="/dashboard/school-setup/constraints"
          icon={AlertTriangle}
        />
      </div>

      <Card>
        <CardHeader>
            <CardTitle className="font-headline">School Profile & Academic Year</CardTitle>
        </CardHeader>
        <CardContent>
            <p className="text-muted-foreground mb-4">Manage your school's general information and academic year settings.</p>
            <Button variant="outline">Edit School Profile</Button>
        </CardContent>
      </Card>
    </div>
  );
}
