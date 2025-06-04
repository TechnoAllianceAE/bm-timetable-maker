'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, PlusCircle, Search, Building } from "lucide-react";

interface MockSchool {
  id: string;
  name: string;
  adminEmail: string;
  status: "Active" | "Pending Setup" | "Suspended";
  subscriptionTier: "Basic" | "Premium" | "Enterprise";
  teachersCount: number;
  studentsCount: number; // Example field from SMS integration
}

const mockSchools: MockSchool[] = [
  { id: "sch001", name: "Greenwood High", adminEmail: "admin_gw@example.com", status: "Active", subscriptionTier: "Premium", teachersCount: 50, studentsCount: 800 },
  { id: "sch002", name: "Oakridge International", adminEmail: "admin_oi@example.com", status: "Active", subscriptionTier: "Enterprise", teachersCount: 75, studentsCount: 1200 },
  { id: "sch003", name: "Valley Public School", adminEmail: "admin_vps@example.com", status: "Pending Setup", subscriptionTier: "Basic", teachersCount: 0, studentsCount: 0 },
  { id: "sch004", name: "City Central School", adminEmail: "admin_ccs@example.com", status: "Suspended", subscriptionTier: "Premium", teachersCount: 60, studentsCount: 950 },
];

export default function ManageSchoolsPage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl flex items-center gap-2"><Building className="text-primary" /> Manage Schools</CardTitle>
          <CardDescription>
            Oversee all schools using K12 Timetable Ace. Add new schools, manage subscriptions, and monitor activity.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            <div className="relative w-full sm:w-auto sm:flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search schools by name or admin email..." className="pl-8 w-full" />
            </div>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
              <PlusCircle className="mr-2 h-4 w-4" /> Add New School
            </Button>
          </div>

          <div className="rounded-lg border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>School Name</TableHead>
                  <TableHead>Admin Email</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Subscription</TableHead>
                  <TableHead className="text-center">Teachers</TableHead>
                  <TableHead className="text-center">Students</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockSchools.map((school) => (
                  <TableRow key={school.id}>
                    <TableCell className="font-medium">{school.name}</TableCell>
                    <TableCell>{school.adminEmail}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={school.status === "Active" ? "outline" : school.status === "Pending Setup" ? "default" : "destructive"}
                        className={school.status === "Active" ? "border-green-500 text-green-600" : ""}
                      >
                        {school.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                       <Badge variant={school.subscriptionTier === "Enterprise" ? "default" : school.subscriptionTier === "Premium" ? "secondary" : "outline"}>
                        {school.subscriptionTier}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">{school.teachersCount}</TableCell>
                    <TableCell className="text-center">{school.studentsCount}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>View Details</DropdownMenuItem>
                          <DropdownMenuItem>Edit School Info</DropdownMenuItem>
                          <DropdownMenuItem>Manage Subscription</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          {school.status !== "Suspended" ? (
                            <DropdownMenuItem className="text-orange-600 focus:text-orange-50 focus:bg-orange-500">Suspend School</DropdownMenuItem>
                          ): (
                            <DropdownMenuItem className="text-green-600 focus:text-green-50 focus:bg-green-500">Reactivate School</DropdownMenuItem>
                          )}
                          <DropdownMenuItem className="text-destructive focus:text-destructive-foreground focus:bg-destructive">Delete School</DropdownMenuItem>
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
