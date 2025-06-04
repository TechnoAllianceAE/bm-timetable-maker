'use server';

/**
 * @fileOverview An AI agent to generate an initial timetable based on school-specific constraints and NEP 2020 guidelines.
 *
 * - generateTimetable - A function that handles the timetable generation process.
 * - GenerateTimetableInput - The input type for the generateTimetable function.
 * - GenerateTimetableOutput - The return type for the generateTimetable function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateTimetableInputSchema = z.object({
  schoolName: z.string().describe('The name of the school.'),
  academicYear: z.string().describe('The academic year for which the timetable is being generated.'),
  stages: z
    .array(
      z.object({
        stageName: z.string().describe('The name of the stage (e.g., Foundational, Preparatory, Middle, Secondary).'),
        grades: z.string().describe('The grades included in this stage (e.g., 1-5).'),
        subjects: z.array(z.string()).describe('The subjects taught in this stage.'),
        minimumSubjectHours: z
          .record(z.number())
          .describe('A map from subject name to the minimum number of hours per week for that subject.'),
      })
    )
    .describe('An array of stages in the school, detailing the grades and subjects taught in each.'),
  teachers: z
    .array(
      z.object({
        teacherName: z.string().describe('The name of the teacher.'),
        subjects: z.array(z.string()).describe('The subjects the teacher can teach.'),
        maxHoursPerWeek: z.number().describe('The maximum number of hours the teacher can teach per week.'),
      })
    )
    .describe('An array of teachers and their details.'),
  classrooms: z
    .array(
      z.object({
        roomName: z.string().describe('The name of the classroom.'),
        capacity: z.number().describe('The capacity of the classroom.'),
      })
    )
    .describe('An array of classrooms and their details.'),
  hardConstraints: z
    .array(z.string())
    .describe(
      'A list of hard constraints that must be satisfied (e.g., no double-booking of teachers or classrooms, minimum/maximum teaching hours for teachers, required subjects per stage as per NEP 2020).'
    ),
  softConstraints: z
    .array(z.string())
    .describe(
      'A list of soft constraints that should be optimized for (e.g., even distribution of teacher workload, preferred time slots for subjects, minimize teacher movement, balanced subject distribution).'
    ),
  schoolPreferences: z.string().describe('Any specific preferences or rules unique to the school.'),
  nep2020Compliance: z
    .string()
    .describe('Details on how the timetable should comply with NEP 2020 guidelines, including curriculum coverage and experiential learning.'),
});

export type GenerateTimetableInput = z.infer<typeof GenerateTimetableInputSchema>;

const GenerateTimetableOutputSchema = z.object({
  timetable: z.string().describe('The generated timetable in a readable format.'),
  summary: z.string().describe('A summary of the timetable, including the number of classes scheduled and any conflicts.'),
  warnings: z.array(z.string()).describe('A list of warnings or potential issues with the timetable.'),
});

export type GenerateTimetableOutput = z.infer<typeof GenerateTimetableOutputSchema>;

export async function generateTimetable(input: GenerateTimetableInput): Promise<GenerateTimetableOutput> {
  return generateTimetableFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateTimetablePrompt',
  input: {schema: GenerateTimetableInputSchema},
  output: {schema: GenerateTimetableOutputSchema},
  prompt: `You are an expert timetable generator for K12 schools, following the NEP 2020 guidelines.

  Generate an initial timetable based on the school-specific constraints and NEP 2020 guidelines provided.

  School Name: {{{schoolName}}}
  Academic Year: {{{academicYear}}}
  Stages: {{{stages}}}
  Teachers: {{{teachers}}}
  Classrooms: {{{classrooms}}}
  Hard Constraints: {{{hardConstraints}}}
  Soft Constraints: {{{softConstraints}}}
  School Preferences: {{{schoolPreferences}}}
  NEP 2020 Compliance: {{{nep2020Compliance}}}

  Ensure the timetable is feasible and optimized according to the given constraints and preferences.

  Output the timetable in a readable format, along with a summary of the timetable and any warnings or potential issues.
  timetable: string
  summary: string
  warnings: array of strings
  `,
});

const generateTimetableFlow = ai.defineFlow(
  {
    name: 'generateTimetableFlow',
    inputSchema: GenerateTimetableInputSchema,
    outputSchema: GenerateTimetableOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
