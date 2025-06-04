'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Save, AlertTriangle, SlidersHorizontal } from "lucide-react";
import Link from "next/link";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

export default function ManageConstraintsPage() {
  const { toast } = useToast();
  const [hardConstraints, setHardConstraints] = useState(
    "No teacher double-booking.\nNo classroom double-booking.\nTeachers: min 10 hours/week, max 30 hours/week.\nRequired subjects per stage must be scheduled."
  );
  const [softConstraints, setSoftConstraints] = useState(
    "Even distribution of teacher workload (max 6 hours/day).\nPrefer Math and Language in morning slots.\nMinimize teacher movement between classes.\nSpread subjects evenly across the week."
  );
   const [nepConstraints, setNepConstraints] = useState(
    "Foundational: Play-based learning, 30-40 min periods.\nPreparatory/Middle: Balanced core skills.\nSecondary: Longer elective periods, teacher expertise matching.\nMinimum weekly hours per subject as per NEP guidelines."
  );


  const handleSaveConstraints = () => {
    // Simulate saving to backend
    console.log({ hardConstraints, softConstraints, nepConstraints });
    toast({
      title: "Constraints Saved",
      description: "School-specific constraints have been updated.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/dashboard/school-setup"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <h1 className="font-headline text-2xl">Manage Constraints & Rules</h1>
      </div>
      <Card>
        <CardHeader>
          <CardDescription>
            Define hard (non-negotiable) and soft (optimization preferences) constraints for timetable generation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="hard-constraints" className="text-lg font-medium flex items-center gap-2 mb-1">
              <AlertTriangle className="text-destructive h-5 w-5" /> Hard Constraints
            </Label>
            <p className="text-sm text-muted-foreground mb-2">These rules must be satisfied by the generated timetable. Enter one rule per line.</p>
            <Textarea
              id="hard-constraints"
              value={hardConstraints}
              onChange={(e) => setHardConstraints(e.target.value)}
              rows={6}
              className="font-code"
            />
          </div>

          <div>
            <Label htmlFor="soft-constraints" className="text-lg font-medium flex items-center gap-2 mb-1">
              <SlidersHorizontal className="text-primary h-5 w-5" /> Soft Constraints (Preferences)
            </Label>
            <p className="text-sm text-muted-foreground mb-2">The AI will try to optimize for these preferences. Enter one rule per line.</p>
            <Textarea
              id="soft-constraints"
              value={softConstraints}
              onChange={(e) => setSoftConstraints(e.target.value)}
              rows={6}
              className="font-code"
            />
          </div>
          
          <div>
            <Label htmlFor="nep-constraints" className="text-lg font-medium flex items-center gap-2 mb-1">
              <FileText className="text-green-600 h-5 w-5" /> NEP 2020 Specific Constraints
            </Label>
            <p className="text-sm text-muted-foreground mb-2">Rules related to NEP 2020 compliance, stage-specific optimizations. Enter one rule per line.</p>
            <Textarea
              id="nep-constraints"
              value={nepConstraints}
              onChange={(e) => setNepConstraints(e.target.value)}
              rows={6}
              className="font-code"
            />
          </div>

          <Button onClick={handleSaveConstraints} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Save className="mr-2 h-4 w-4" /> Save All Constraints
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
