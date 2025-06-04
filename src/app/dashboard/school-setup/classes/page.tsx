'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, PlusCircle, Search, ArrowLeft, Users } from "lucide-react";
import Link from "next/link";

interface MockClass {
  id: string;
  name: string; // e.g., Grade 9 - Section A
  gradeLevel: string; // e.g., Grade 9
  section: string; // e.g., A
  classTeacher?: string; // Teacher ID or Name
  studentCount: number;
  stage: "Foundational" | "Preparatory" | "Middle" | "Secondary";
}

const mockClasses: MockClass[] = [
  { id: "CLS001", name: "Grade 1 - Rose", gradeLevel: "Grade 1", section: "Rose", classTeacher: "Ms. Diya", studentCount: 28, stage: "Foundational" },
  { id: "CLS002", name: "Grade 6 - Alpha", gradeLevel: "Grade 6", section: "Alpha", classTeacher: "Mr. Ben", studentCount: 32, stage: "Preparatory" },
  { id: "CLS003", name: "Grade 9 - Titans", gradeLevel: "Grade 9", section: "Titans", classTeacher: "Ms. Carol", studentCount: 35, stage: "Middle" },
  { id: "CLS004", name: "Grade 11 - Science", gradeLevel: "Grade 11", section: "Science", classTeacher: "Mr. Evan", studentCount: 30, stage: "Secondary" },
];

export default function ManageClassesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/dashboard/school-setup"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <h1 className="font-headline text-2xl">Manage Classes & Sections</h1>
      </div>
      <Card>
        <CardHeader>
          <CardDescription>
            Define classes, sections, assign class teachers, and manage student groups for timetable purposes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            <div className="relative w-full sm:w-auto sm:flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search classes..." className="pl-8 w-full" />
            </div>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
              <PlusCircle className="mr-2 h-4 w-4" /> Add New Class/Section
            </Button>
          </div>

          <div className="rounded-lg border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Class Name</TableHead>
                  <TableHead>Grade Level</TableHead>
                  <TableHead>Section</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Class Teacher</TableHead>
                  <TableHead className="text-center">Students</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockClasses.map((cls) => (
                  <TableRow key={cls.id}>
                    <TableCell className="font-medium">{cls.name}</TableCell>
                    <TableCell>{cls.gradeLevel}</TableCell>
                    <TableCell>{cls.section}</TableCell>
                    <TableCell><Badge variant="outline">{cls.stage}</Badge></TableCell>
                    <TableCell>{cls.classTeacher ?? 'N/A'}</TableCell>
                    <TableCell className="text-center">{cls.studentCount}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>Edit Class</DropdownMenuItem>
                          <DropdownMenuItem>Assign Subjects</DropdownMenuItem>
                          <DropdownMenuItem>Manage Students (Link to SMS)</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive focus:text-destructive-foreground focus:bg-destructive">Delete Class</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
