'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Save } from "lucide-react";
import { useState } from "react";

export default function PreferencesPage() {
  const [preferredSlots, setPreferredSlots] = useState<string[]>([]);
  const [preferredSubjects, setPreferredSubjects] = useState<string[]>([]);
  const [otherNotes, setOtherNotes] = useState('');
  const { toast } = useToast();

  const handlePreferredSlotChange = (slot: string) => {
    setPreferredSlots(prev => 
      prev.includes(slot) ? prev.filter(s => s !== slot) : [...prev, slot]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate API call
    console.log({ preferredSlots, preferredSubjects, otherNotes });
    toast({
      title: "Preferences Saved",
      description: "Your preferences have been updated and will be considered for future timetables.",
    });
  };

  const timeSlots = ["Morning (9 AM - 12 PM)", "Afternoon (1 PM - 4 PM)"];
  const subjects = ["Mathematics", "Physics", "Chemistry", "English", "History"];

  return (
    <div className="space-y-6">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="font-headline text-2xl">My Preferences</CardTitle>
          <CardDescription>
            Set your preferred time slots, subjects, or any other considerations for timetable generation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <Label className="text-base font-medium">Preferred Time Slots</Label>
              <p className="text-sm text-muted-foreground mb-2">Select time slots you prefer to teach in.</p>
              <div className="space-y-2">
                {timeSlots.map(slot => (
                  <div key={slot} className="flex items-center space-x-2">
                    <Checkbox
                      id={`slot-${slot}`}
                      checked={preferredSlots.includes(slot)}
                      onCheckedChange={() => handlePreferredSlotChange(slot)}
                    />
                    <Label htmlFor={`slot-${slot}`} className="font-normal">{slot}</Label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="preferred-subjects" className="text-base font-medium">Preferred Subjects (if applicable)</Label>
              <p className="text-sm text-muted-foreground mb-2">Indicate subjects you have a strong preference for teaching, if you teach multiple.</p>
              {/* This could be a multi-select component in a real app */}
              <Select onValueChange={(value) => setPreferredSubjects(value ? [value] : [])}>
                <SelectTrigger id="preferred-subjects">
                  <SelectValue placeholder="Select a preferred subject" />
                </SelectTrigger>
                <SelectContent>
                  {subjects.map(subject => (
                    <SelectItem key={subject} value={subject}>{subject}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
               <p className="text-xs text-muted-foreground mt-1">For multiple subjects, please list in 'Other Notes'.</p>
            </div>

            <div>
              <Label htmlFor="other-notes" className="text-base font-medium">Other Notes or Constraints</Label>
              <p className="text-sm text-muted-foreground mb-2">Any other specific requests or constraints (e.g., "Prefer not to have back-to-back lab sessions").</p>
              <Textarea
                id="other-notes"
                value={otherNotes}
                onChange={(e) => setOtherNotes(e.target.value)}
                placeholder="Enter any additional notes here..."
                rows={4}
              />
            </div>
            
            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
              <Save className="mr-2 h-4 w-4" /> Save Preferences
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
