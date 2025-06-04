'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { Save, KeyRound, UserCircle2, Bell } from "lucide-react";
import { Switch } from "@/components/ui/switch";

export default function AccountSettingsPage() {
  const { user } = useAuth();
  const { toast } = useToast();

  const handleProfileUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate API call
    toast({
      title: "Profile Updated",
      description: "Your profile information has been successfully updated.",
    });
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate API call
    toast({
      title: "Password Changed",
      description: "Your password has been successfully updated. Please log in again if prompted.",
      variant: "default" 
    });
     // Ideally, clear password fields here
  };
  
  const handleNotificationSettingsUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Notification Settings Updated",
      description: "Your notification preferences have been saved.",
    });
  };


  if (!user) {
    return <p>Loading user data...</p>; // Or a proper loader
  }

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Account Settings</CardTitle>
          <CardDescription>
            Manage your personal profile, password, and notification preferences.
          </CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><UserCircle2 className="text-primary"/> Profile Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input id="name" defaultValue={user.name} className="mt-1"/>
            </div>
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input id="email" type="email" defaultValue={user.email} disabled className="mt-1"/>
              <p className="text-xs text-muted-foreground mt-1">Email address cannot be changed.</p>
            </div>
            {user.role !== 'Super Admin' && user.schoolId && (
              <div>
                <Label htmlFor="schoolId">School ID</Label>
                <Input id="schoolId" defaultValue={user.schoolId} disabled className="mt-1"/>
              </div>
            )}
            <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Save className="mr-2 h-4 w-4" /> Update Profile
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><KeyRound className="text-primary"/> Change Password</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <Label htmlFor="current-password">Current Password</Label>
              <Input id="current-password" type="password" required className="mt-1"/>
            </div>
            <div>
              <Label htmlFor="new-password">New Password</Label>
              <Input id="new-password" type="password" required className="mt-1"/>
            </div>
            <div>
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input id="confirm-password" type="password" required className="mt-1"/>
            </div>
            <Button type="submit" variant="outline" className="border-primary text-primary hover:bg-primary/10">
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-lg flex items-center gap-2"><Bell className="text-primary"/> Notification Preferences</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleNotificationSettingsUpdate} className="space-y-4">
            <div className="flex items-center justify-between space-x-2 p-3 border rounded-lg">
                <Label htmlFor="email-notifications" className="flex flex-col space-y-1">
                <span>Email Notifications</span>
                <span className="font-normal leading-snug text-muted-foreground">
                    Receive important updates and alerts via email.
                </span>
                </Label>
                <Switch id="email-notifications" defaultChecked />
            </div>
             <div className="flex items-center justify-between space-x-2 p-3 border rounded-lg">
                <Label htmlFor="inapp-notifications" className="flex flex-col space-y-1">
                <span>In-App Notifications</span>
                <span className="font-normal leading-snug text-muted-foreground">
                    Get notified within the K12 Timetable Ace platform.
                </span>
                </Label>
                <Switch id="inapp-notifications" defaultChecked />
            </div>
            <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Save className="mr-2 h-4 w-4" /> Save Notification Preferences
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
