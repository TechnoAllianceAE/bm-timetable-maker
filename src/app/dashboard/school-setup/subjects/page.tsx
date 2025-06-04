'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, PlusCircle, Search, ArrowLeft, FileText } from "lucide-react";
import Link from "next/link";

interface MockSubject {
  id: string;
  name: string;
  code: string;
  stage: "Foundational" | "Preparatory" | "Middle" | "Secondary" | "All";
  weeklyHoursRequired?: number; // NEP 2020 minimum hours
  type: "Core" | "Elective" | "Vocational" | "Activity";
}

const mockSubjects: MockSubject[] = [
  { id: "SUB001", name: "Mathematics", code: "MATH101", stage: "All", weeklyHoursRequired: 4, type: "Core" },
  { id: "SUB002", name: "English Language", code: "ENG101", stage: "All", weeklyHoursRequired: 4, type: "Core" },
  { id: "SUB003", name: "Physics", code: "PHY201", stage: "Secondary", weeklyHoursRequired: 3, type: "Core" },
  { id: "SUB004", name: "Environmental Studies (EVS)", code: "EVS001", stage: "Foundational", weeklyHoursRequired: 3, type: "Core" },
  { id: "SUB005", name: "Introduction to AI", code: "AI301", stage: "Middle", type: "Elective" },
  { id: "SUB006", name: "Pottery", code: "VOC101", stage: "Middle", type: "Vocational" },
];

export default function ManageSubjectsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/dashboard/school-setup"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <h1 className="font-headline text-2xl">Manage Subjects & Courses</h1>
      </div>
      <Card>
        <CardHeader>
          <CardDescription>
            Define subjects, courses, their codes, and relevance to different NEP 2020 stages.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            <div className="relative w-full sm:w-auto sm:flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search subjects..." className="pl-8 w-full" />
            </div>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
              <PlusCircle className="mr-2 h-4 w-4" /> Add New Subject/Course
            </Button>
          </div>

          <div className="rounded-lg border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Subject Name</TableHead>
                  <TableHead>Code</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-center">Min. Weekly Hrs</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockSubjects.map((subject) => (
                  <TableRow key={subject.id}>
                    <TableCell className="font-medium">{subject.name}</TableCell>
                    <TableCell>{subject.code}</TableCell>
                    <TableCell><Badge variant="outline">{subject.stage}</Badge></TableCell>
                    <TableCell><Badge variant="secondary">{subject.type}</Badge></TableCell>
                    <TableCell className="text-center">{subject.weeklyHoursRequired ?? '-'}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>Edit Subject</DropdownMenuItem>
                          <DropdownMenuItem>Assign to Grades</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive focus:text-destructive-foreground focus:bg-destructive">Delete Subject</DropdownMenuItem>
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
