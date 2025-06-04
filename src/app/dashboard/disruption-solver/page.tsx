'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, AlertTriangle, Sparkles } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { solveDisruption, type SolveDisruptionInput } from '@/ai/flows/solve-disruptions';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const formSchema = z.object({
  absentTeacherId: z.string().min(1, "Absent teacher ID is required"),
  courseId: z.string().min(1, "Course ID is required"),
  timeSlot: z.string().min(1, "Time slot is required"),
  schoolId: z.string().min(1, "School ID is required"),
});

type DisruptionSolverFormValues = z.infer<typeof formSchema>;

export default function DisruptionSolverPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [solution, setSolution] = useState<string | null>(null);
  const { toast } = useToast();

  const form = useForm<DisruptionSolverFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      absentTeacherId: "TCH001",
      courseId: "MATH101",
      timeSlot: "Monday 09:00-10:00",
      schoolId: "SCH001",
    },
  });

  const onSubmit = async (values: DisruptionSolverFormValues) => {
    setIsLoading(true);
    setSolution(null);
    try {
      const input: SolveDisruptionInput = values;
      const result = await solveDisruption(input);
      setSolution(`Suggested Replacement: ${result.suggestedReplacementTeacherId}\nJustification: ${result.justification}`);
      toast({
        title: "Disruption Solved",
        description: "AI has suggested a solution for the timetable disruption.",
      });
    } catch (error) {
      console.error("Error solving disruption:", error);
      toast({
        title: "Solving Failed",
        description: error instanceof Error ? error.message : "An unknown error occurred.",
        variant: "destructive",
      });
    }
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl flex items-center gap-2"><AlertTriangle className="text-destructive" /> AI Disruption Solver</CardTitle>
          <CardDescription>
            Report a disruption (e.g., teacher absence) and get AI-powered suggestions for adjustments.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="absentTeacherId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Absent Teacher ID</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="courseId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Course ID (affected)</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="timeSlot"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Time Slot</FormLabel>
                    <FormControl><Input {...field} placeholder="e.g., Monday 10:00-11:00" /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="schoolId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>School ID</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground" disabled={isLoading}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                Find Solution
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {solution && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="font-headline">Suggested Solution</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="p-4 bg-muted rounded-md overflow-x-auto text-sm">{solution}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
