'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { CalendarIcon, Send } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { DateRange } from "react-day-picker";

export default function ReportAbsencePage() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [reason, setReason] = useState('');
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!dateRange || !dateRange.from) {
      toast({ title: "Error", description: "Please select an absence date or range.", variant: "destructive"});
      return;
    }
    if (!reason.trim()) {
      toast({ title: "Error", description: "Please provide a reason for absence.", variant: "destructive"});
      return;
    }
    // Simulate API call
    console.log({
      startDate: dateRange.from,
      endDate: dateRange.to,
      reason,
    });
    toast({
      title: "Absence Reported",
      description: `Your absence from ${format(dateRange.from, "PPP")}${dateRange.to ? ` to ${format(dateRange.to, "PPP")}`: ""} has been reported.`,
    });
    setDateRange(undefined);
    setReason('');
  };

  return (
    <div className="space-y-6">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Report Absence</CardTitle>
          <CardDescription>
            Notify administration about your upcoming absence. This will trigger the AI disruption solver.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="absence-dates">Absence Date(s)</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    id="absence-dates"
                    variant={"outline"}
                    className={cn(
                      "w-full justify-start text-left font-normal mt-1",
                      !dateRange && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateRange?.from ? (
                      dateRange.to ? (
                        <>
                          {format(dateRange.from, "LLL dd, y")} -{" "}
                          {format(dateRange.to, "LLL dd, y")}
                        </>
                      ) : (
                        format(dateRange.from, "LLL dd, y")
                      )
                    ) : (
                      <span>Pick a date or range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={dateRange?.from}
                    selected={dateRange}
                    onSelect={setDateRange}
                    numberOfMonths={2}
                    disabled={(date) => date < new Date(new Date().setDate(new Date().getDate() -1)) } // Disable past dates
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div>
              <Label htmlFor="reason">Reason for Absence</Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Please provide a brief reason (e.g., Personal leave, Sick leave)"
                className="mt-1"
                rows={4}
              />
            </div>
            
            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
              <Send className="mr-2 h-4 w-4" /> Submit Absence Report
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
