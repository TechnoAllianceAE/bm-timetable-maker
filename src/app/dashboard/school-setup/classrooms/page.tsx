'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, PlusCircle, Search, ArrowLeft, BookOpen } from "lucide-react";
import Link from "next/link";

interface MockClassroom {
  id: string;
  name: string;
  capacity: number;
  type: "Classroom" | "Lab" | "Hall" | "Activity Room";
  features: string[]; // e.g., Projector, Whiteboard, Computers
  status: "Available" | "Under Maintenance";
}

const mockClassrooms: MockClassroom[] = [
  { id: "C101", name: "Room 101", capacity: 30, type: "Classroom", features: ["Projector", "Whiteboard"], status: "Available" },
  { id: "L201", name: "Science Lab A", capacity: 25, type: "Lab", features: ["Gas Taps", "Sinks", "Microscopes"], status: "Available" },
  { id: "H301", name: "Assembly Hall", capacity: 200, type: "Hall", features: ["Stage", "Audio System"], status: "Under Maintenance" },
  { id: "A102", name: "Art Room", capacity: 20, type: "Activity Room", features: ["Sinks", "Storage"], status: "Available" },
];

export default function ManageClassroomsPage() {
  return (
    <div className="space-y-6">
       <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/dashboard/school-setup"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <h1 className="font-headline text-2xl">Manage Classrooms & Venues</h1>
      </div>
      <Card>
        <CardHeader>
          <CardDescription>
            Define and manage all teaching spaces, labs, and other venues within the school.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            <div className="relative w-full sm:w-auto sm:flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search classrooms..." className="pl-8 w-full" />
            </div>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto">
              <PlusCircle className="mr-2 h-4 w-4" /> Add New Classroom/Venue
            </Button>
          </div>

          <div className="rounded-lg border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-center">Capacity</TableHead>
                  <TableHead>Features</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockClassrooms.map((room) => (
                  <TableRow key={room.id}>
                    <TableCell className="font-medium">{room.name}</TableCell>
                    <TableCell><Badge variant="outline">{room.type}</Badge></TableCell>
                    <TableCell className="text-center">{room.capacity}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {room.features.map(feature => <Badge key={feature} variant="secondary" className="text-xs">{feature}</Badge>)}
                      </div>
                    </TableCell>
                    <TableCell>
                       <Badge variant={room.status === "Available" ? "outline" : "destructive"} 
                              className={room.status === "Available" ? "border-green-500 text-green-600" : ""}>
                        {room.status}
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
                          <DropdownMenuItem>Edit Classroom</DropdownMenuItem>
                          <DropdownMenuItem>Set Unavailability</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive focus:text-destructive-foreground focus:bg-destructive">Delete Classroom</DropdownMenuItem>
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
