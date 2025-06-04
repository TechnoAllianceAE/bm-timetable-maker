'use server';

/**
 * @fileOverview AI flow to solve timetable disruptions caused by teacher absences.
 *
 * - solveDisruption - A function to get AI-recommended timetable adjustments for teacher absences.
 * - SolveDisruptionInput - The input type for the solveDisruption function.
 * - SolveDisruptionOutput - The return type for the solveDisruption function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SolveDisruptionInputSchema = z.object({
  absentTeacherId: z.string().describe('The ID of the absent teacher.'),
  courseId: z.string().describe('The ID of the course that needs a replacement teacher.'),
  timeSlot: z.string().describe('The time slot when the teacher is absent.'),
  schoolId: z.string().describe('The ID of the school where the disruption occurred.'),
});
export type SolveDisruptionInput = z.infer<typeof SolveDisruptionInputSchema>;

const SolveDisruptionOutputSchema = z.object({
  suggestedReplacementTeacherId: z
    .string()
    .describe('The ID of the suggested replacement teacher.'),
  justification: z
    .string()
    .describe('The AI justification for the suggested replacement.'),
});
export type SolveDisruptionOutput = z.infer<typeof SolveDisruptionOutputSchema>;

export async function solveDisruption(input: SolveDisruptionInput): Promise<SolveDisruptionOutput> {
  return solveDisruptionFlow(input);
}

const solveDisruptionPrompt = ai.definePrompt({
  name: 'solveDisruptionPrompt',
  input: {schema: SolveDisruptionInputSchema},
  output: {schema: SolveDisruptionOutputSchema},
  prompt: `You are an AI timetable assistant helping to solve disruptions caused by teacher absences.

  Given the following information about a teacher absence, suggest a replacement teacher and justify your suggestion.

  Absent Teacher ID: {{{absentTeacherId}}}
  Course ID: {{{courseId}}}
  Time Slot: {{{timeSlot}}}
  School ID: {{{schoolId}}}

  Consider factors such as teacher availability, subject expertise, and minimizing disruption to the existing timetable.

  Return the ID of the suggested replacement teacher and a brief justification for your choice.
`,
});

const solveDisruptionFlow = ai.defineFlow(
  {
    name: 'solveDisruptionFlow',
    inputSchema: SolveDisruptionInputSchema,
    outputSchema: SolveDisruptionOutputSchema,
  },
  async input => {
    const {output} = await solveDisruptionPrompt(input);
    return output!;
  }
);
