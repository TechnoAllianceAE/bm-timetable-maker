'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Save, Bell, Database, ShieldCheck, Users } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

export default function GlobalSettingsPage() {
  const { toast } = useToast();

  const handleSaveSettings = (settingName: string) => {
    // Simulate saving settings
    toast({
      title: "Settings Saved",
      description: `${settingName} have been updated successfully.`,
    });
  };

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Global System Settings</CardTitle>
          <CardDescription>
            Manage system-wide configurations, default parameters, and integrations. (Super Admin Access)
          </CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><Users className="text-primary"/> School Management</CardTitle>
          <CardDescription>Oversee and manage all registered schools in the system.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-muted-foreground">View a list of all schools, add new schools, or manage existing school configurations.</p>
          <Button asChild>
            <Link href="/dashboard/manage-schools">Manage Schools</Link>
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><Bell className="text-primary"/> Notification Settings</CardTitle>
          <CardDescription>Configure global email templates and notification triggers.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between space-x-2 p-3 border rounded-lg">
            <Label htmlFor="master-notifications" className="flex flex-col space-y-1">
              <span>Master Notification Switch</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Enable or disable all system notifications globally.
              </span>
            </Label>
            <Switch id="master-notifications" defaultChecked />
          </div>
          <div>
            <Label htmlFor="admin-email">System Admin Email</Label>
            <Input id="admin-email" type="email" defaultValue="sysadmin@k12timetable.ace" className="mt-1"/>
          </div>
          <Button onClick={() => handleSaveSettings("Notification Settings")} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Save className="mr-2 h-4 w-4" /> Save Notification Settings
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><Database className="text-primary"/> Default Parameters</CardTitle>
          <CardDescription>Set default values for new schools (e.g., max teacher hours).</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
           <div>
            <Label htmlFor="default-max-hours">Default Max Teacher Hours/Week</Label>
            <Input id="default-max-hours" type="number" defaultValue="30" className="mt-1"/>
          </div>
           <div>
            <Label htmlFor="default-min-hours">Default Min Teacher Hours/Week</Label>
            <Input id="default-min-hours" type="number" defaultValue="10" className="mt-1"/>
          </div>
          <Button onClick={() => handleSaveSettings("Default Parameters")} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Save className="mr-2 h-4 w-4" /> Save Default Parameters
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><ShieldCheck className="text-primary"/> Security & Compliance</CardTitle>
          <CardDescription>Manage data retention policies and system security configurations.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="data-retention">Data Retention Period (Days)</Label>
            <Input id="data-retention" type="number" defaultValue="365" className="mt-1"/>
          </div>
           <div className="flex items-center justify-between space-x-2 p-3 border rounded-lg">
            <Label htmlFor="audit-logs" className="flex flex-col space-y-1">
              <span>Enable Audit Logs</span>
              <span className="font-normal leading-snug text-muted-foreground">
                Track significant actions performed by users.
              </span>
            </Label>
            <Switch id="audit-logs" defaultChecked />
          </div>
          <Button onClick={() => handleSaveSettings("Security Settings")} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            <Save className="mr-2 h-4 w-4" /> Save Security Settings
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
