'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { CalendarDays, ListFilter } from "lucide-react";
import Image from "next/image";

// Mock data for demonstration
const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const timeSlots = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00"];

const teacherSchedule = {
  Monday: { "09:00-10:00": { subject: "Math", class: "Grade 9A", room: "101" } },
  Tuesday: { "10:00-11:00": { subject: "Math", class: "Grade 10B", room: "101" } },
  Wednesday: { "13:00-14:00": { subject: "Physics Lab", class: "Grade 11", room: "Lab 2" } },
  // ... more data
};

export default function MySchedulePage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">My Schedule</CardTitle>
          <CardDescription>
            View your personal teaching schedule for the week or month.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="weekly" className="w-full">
            <div className="flex justify-between items-center mb-4">
              <TabsList>
                <TabsTrigger value="weekly">Weekly View</TabsTrigger>
                <TabsTrigger value="monthly">Monthly View</TabsTrigger>
              </TabsList>
              <div className="flex gap-2">
                <Button variant="outline"><ListFilter className="mr-2 h-4 w-4"/> Filter</Button>
                <Button variant="outline"><CalendarDays className="mr-2 h-4 w-4"/> Export</Button>
              </div>
            </div>
            
            <TabsContent value="weekly">
              <Card>
                <CardHeader>
                  <CardTitle className="font-headline">Current Week</CardTitle>
                </CardHeader>
                <CardContent className="overflow-x-auto">
                  <Table className="min-w-full">
                    <TableHeader>
                      <TableRow className="bg-muted">
                        <TableHead className="w-[120px]">Time</TableHead>
                        {daysOfWeek.map(day => (
                          <TableHead key={day} className="min-w-[180px]">{day}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {timeSlots.map(slot => (
                        <TableRow key={slot}>
                          <TableCell className="font-medium bg-muted/50">{slot}</TableCell>
                          {daysOfWeek.map(day => {
                            const entry = teacherSchedule[day as keyof typeof teacherSchedule]?.[slot as keyof typeof teacherSchedule.Monday];
                            return (
                              <TableCell key={`${day}-${slot}`} className="p-1 align-top h-24">
                                {entry ? (
                                  <Card className="h-full p-2 bg-primary/10 border-primary/30">
                                    <p className="font-semibold text-sm text-primary">{entry.subject}</p>
                                    <p className="text-xs text-primary/80">{entry.class}</p>
                                    <p className="text-xs text-primary/80">Room: {entry.room}</p>
                                  </Card>
                                ) : (
                                  <div className="h-full border border-dashed rounded-md flex items-center justify-center text-muted-foreground/30">
                                    -
                                  </div>
                                )}
                              </TableCell>
                            );
                          })}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="monthly">
              <Card>
                <CardHeader>
                  <CardTitle className="font-headline">Monthly Calendar</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <p className="text-muted-foreground mb-4">A monthly calendar view will be displayed here.</p>
                  <Image src="https://placehold.co/800x500.png" alt="Monthly Calendar Placeholder" width={800} height={500} className="rounded-md border mx-auto" data-ai-hint="calendar month"/>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
