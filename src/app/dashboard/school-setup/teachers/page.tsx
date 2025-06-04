'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, UserPlus, Search, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface MockTeacher {
  id: string;
  name: string;
  employeeId: string;
  subjects: string[];
  maxHours: number;
  status: "Active" | "On Leave" | "Inactive";
}

const mockTeachers: MockTeacher[] = [
  { id: "T001", name: "Priya Sharma", employeeId: "EMP101", subjects: ["Mathematics", "Physics"], maxHours: 25, status: "Active" },
  { id: "T002", name: "Rahul Verma", employeeId: "EMP102", subjects: ["English", "History"], maxHours: 22, status: "Active" },
  { id: "T003", name: "Anjali Mehta", employeeId: "EMP103", subjects: ["Chemistry", "Biology"], maxHours: 20, status: "On Leave" },
  { id: "T004", name: "Suresh Kumar", employeeId: "EMP104", subjects: ["Physical Education"], maxHours: 18, status: "Active" },
];

export default function ManageTeachersPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/dashboard/school-setup"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <h1 className="font-headline text-2xl">Manage Teachers</h1>
      </div>
      <Card>
        <CardHeader>
          <CardDescription>
            Add, edit, and manage teacher profiles, their subject expertise, and teaching constraints.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            <div className="relative w-full sm:w-auto sm:flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search teachers..." className="pl-8 w-full" />
            </div>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
              <UserPlus className="mr-2 h-4 w-4" /> Add New Teacher
            </Button>
          </div>

          <div className="rounded-lg border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Employee ID</TableHead>
                  <TableHead>Subjects</TableHead>
                  <TableHead>Max Hours/Week</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockTeachers.map((teacher) => (
                  <TableRow key={teacher.id}>
                    <TableCell className="font-medium">{teacher.name}</TableCell>
                    <TableCell>{teacher.employeeId}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {teacher.subjects.map(subject => <Badge key={subject} variant="secondary">{subject}</Badge>)}
                      </div>
                    </TableCell>
                    <TableCell>{teacher.maxHours}</TableCell>
                    <TableCell>
                       <Badge variant={teacher.status === "Active" ? "outline" : teacher.status === "On Leave" ? "default" : "destructive"} 
                              className={teacher.status === "Active" ? "border-green-500 text-green-600" : ""}>
                        {teacher.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>Edit Teacher</DropdownMenuItem>
                          <DropdownMenuItem>Set Availability</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive focus:text-destructive-foreground focus:bg-destructive">Deactivate Teacher</DropdownMenuItem>
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
