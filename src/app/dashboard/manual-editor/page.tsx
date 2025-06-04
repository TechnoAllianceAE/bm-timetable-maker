'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { GripVertical, Edit3, Trash2 } from "lucide-react";
import Image from "next/image";

// Mock data for demonstration
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const timeSlots = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00"];

const initialTimetableData = {
  Monday: {
    "09:00-10:00": { subject: "Math", teacher: "Ms. A", class: "Grade 9A", room: "101" },
    "10:00-11:00": { subject: "Science", teacher: "Mr. B", class: "Grade 9A", room: "Lab 1" },
  },
  Tuesday: {
    "11:00-12:00": { subject: "English", teacher: "Ms. C", class: "Grade 10B", room: "202" },
  },
  // ... more data
};


export default function ManualEditorPage() {
  // In a real app, this would use React DnD and state management (e.g., Redux Toolkit)
  // For this placeholder, we'll just display a static table.

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Manual Timetable Editor</CardTitle>
          <CardDescription>
            Drag and drop classes to adjust the timetable. Conflicts will be highlighted in real-time.
            (Drag and drop functionality is a conceptual representation here.)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <div>
              <Button variant="outline" className="mr-2">Load Timetable</Button>
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Save Changes</Button>
            </div>
            <Badge variant="destructive">3 Conflicts Detected</Badge>
          </div>

          <div className="overflow-x-auto rounded-lg border">
            <Table className="min-w-full">
              <TableHeader>
                <TableRow className="bg-muted">
                  <TableHead className="w-[120px]">Time Slot</TableHead>
                  {days.map(day => (
                    <TableHead key={day} className="min-w-[200px]">{day}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {timeSlots.map(slot => (
                  <TableRow key={slot}>
                    <TableCell className="font-medium bg-muted/50">{slot}</TableCell>
                    {days.map(day => {
                      const entry = initialTimetableData[day as keyof typeof initialTimetableData]?.[slot as keyof typeof initialTimetableData.Monday];
                      return (
                        <TableCell key={`${day}-${slot}`} className="p-1 align-top h-32">
                          {entry ? (
                            <Card className="h-full flex flex-col justify-between p-2 cursor-grab bg-card hover:shadow-md transition-shadow">
                              <div className="flex items-start justify-between">
                                <GripVertical className="h-4 w-4 text-muted-foreground mr-1 shrink-0" />
                                <div className="flex-grow">
                                  <p className="font-semibold text-sm">{entry.subject}</p>
                                  <p className="text-xs text-muted-foreground">{entry.teacher}</p>
                                  <p className="text-xs text-muted-foreground">{entry.class} / {entry.room}</p>
                                </div>
                                <div className="flex flex-col space-y-1">
                                   <Button variant="ghost" size="icon" className="h-6 w-6"><Edit3 className="h-3 w-3" /></Button>
                                   <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive"><Trash2 className="h-3 w-3" /></Button>
                                </div>
                              </div>
                            </Card>
                          ) : (
                            <div className="h-full border border-dashed rounded-md flex items-center justify-center text-muted-foreground/50">
                              Empty
                            </div>
                          )}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-4 p-4 border rounded-lg bg-yellow-50 border-yellow-200">
             <p className="text-sm text-yellow-700 font-medium">
                <span className="font-bold">Note:</span> The drag-and-drop interface shown above is a visual representation. Full interactivity requires `react-dnd` and state management libraries.
             </p>
          </div>
           <div className="mt-6">
            <h3 className="font-headline text-lg mb-2">Concept Image</h3>
            <Image src="https://placehold.co/800x400.png" alt="Timetable Grid Example" width={800} height={400} className="rounded-md border" data-ai-hint="timetable grid" />
            <p className="text-sm text-muted-foreground mt-2">Conceptual representation of a filled timetable grid.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
