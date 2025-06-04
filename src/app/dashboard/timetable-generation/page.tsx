'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Wand2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { generateTimetable, type GenerateTimetableInput } from '@/ai/flows/generate-timetable';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const formSchema = z.object({
  schoolName: z.string().min(1, "School name is required"),
  academicYear: z.string().min(1, "Academic year is required"),
  stages: z.string().min(1, "Stage details are required (JSON format)"), // Simplified for demo
  teachers: z.string().min(1, "Teacher details are required (JSON format)"),
  classrooms: z.string().min(1, "Classroom details are required (JSON format)"),
  hardConstraints: z.string().min(1, "Hard constraints are required"),
  softConstraints: z.string().min(1, "Soft constraints are required"),
  schoolPreferences: z.string().optional(),
  nep2020Compliance: z.string().min(1, "NEP 2020 compliance details are required"),
});

type TimetableGenerationFormValues = z.infer<typeof formSchema>;

export default function TimetableGenerationPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [generatedTimetable, setGeneratedTimetable] = useState<string | null>(null);
  const { toast } = useToast();

  const form = useForm<TimetableGenerationFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      schoolName: "Demo School",
      academicYear: "2024-2025",
      stages: JSON.stringify([{ stageName: "Foundational", grades: "1-2", subjects: ["Language", "Math"], minimumSubjectHours: {"Language": 5, "Math": 5} }], null, 2),
      teachers: JSON.stringify([{ teacherName: "Ms. Priya", subjects: ["Math"], maxHoursPerWeek: 20 }], null, 2),
      classrooms: JSON.stringify([{ roomName: "Room 101", capacity: 30 }], null, 2),
      hardConstraints: "No teacher double booking. Max 25 hours per teacher.",
      softConstraints: "Prefer Math in mornings. Balance teacher load.",
      schoolPreferences: "No classes after 3 PM on Fridays.",
      nep2020Compliance: "Ensure 30 min play activity daily for Foundational stage.",
    },
  });

  const onSubmit = async (values: TimetableGenerationFormValues) => {
    setIsLoading(true);
    setGeneratedTimetable(null);
    try {
      // Attempt to parse JSON string fields
      const parsedStages = JSON.parse(values.stages);
      const parsedTeachers = JSON.parse(values.teachers);
      const parsedClassrooms = JSON.parse(values.classrooms);

      const input: GenerateTimetableInput = {
        ...values,
        stages: parsedStages,
        teachers: parsedTeachers,
        classrooms: parsedClassrooms,
        hardConstraints: values.hardConstraints.split('\n'),
        softConstraints: values.softConstraints.split('\n'),
      };
      
      const result = await generateTimetable(input);
      setGeneratedTimetable(`Summary: ${result.summary}\n\nTimetable:\n${result.timetable}\n\nWarnings: ${result.warnings.join(', ')}`);
      toast({
        title: "Timetable Generated",
        description: "AI has successfully generated a new timetable.",
      });
    } catch (error) {
      console.error("Error generating timetable:", error);
      let errorMessage = "Failed to generate timetable. Please check your input.";
      if (error instanceof SyntaxError) {
        errorMessage = "Invalid JSON format in one of the fields. Please correct it.";
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast({
        title: "Generation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    }
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">AI Timetable Generation</CardTitle>
          <CardDescription>
            Provide school data and constraints to generate an optimized timetable using AI.
            All array/object inputs should be in valid JSON format.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="schoolName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>School Name</FormLabel>
                      <FormControl><Input {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="academicYear"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Academic Year</FormLabel>
                      <FormControl><Input {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              
              <FormField
                control={form.control}
                name="stages"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Stages (JSON format)</FormLabel>
                    <FormControl><Textarea {...field} rows={5} placeholder='[{"stageName": "Foundational", ...}]' /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="teachers"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Teachers (JSON format)</FormLabel>
                    <FormControl><Textarea {...field} rows={5} placeholder='[{"teacherName": "Mr. X", ...}]' /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="classrooms"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Classrooms (JSON format)</FormLabel>
                    <FormControl><Textarea {...field} rows={3} placeholder='[{"roomName": "Room A", ...}]' /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="hardConstraints"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Hard Constraints (one per line)</FormLabel>
                    <FormControl><Textarea {...field} rows={3} placeholder="No double booking of teachers..." /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="softConstraints"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Soft Constraints (one per line)</FormLabel>
                    <FormControl><Textarea {...field} rows={3} placeholder="Prefer Math in mornings..." /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="schoolPreferences"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>School Preferences</FormLabel>
                    <FormControl><Textarea {...field} rows={2} placeholder="e.g., Specific assembly times" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="nep2020Compliance"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>NEP 2020 Compliance Details</FormLabel>
                    <FormControl><Textarea {...field} rows={3} placeholder="Details on curriculum coverage, experiential learning..." /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground" disabled={isLoading}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                Generate Timetable
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {generatedTimetable && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="font-headline">Generated Timetable Output</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="p-4 bg-muted rounded-md overflow-x-auto text-sm">{generatedTimetable}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
