'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, LineChart, PieChart, Users, BookOpen, AlertTriangle, CheckSquare } from "lucide-react";
import { ResponsiveContainer, Bar, XAxis, YAxis, Tooltip, Legend, Line, Pie, Cell } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@/components/ui/chart';

const teacherUtilizationData = [
  { name: 'Ms. A', hours: 25, maxHours: 30 },
  { name: 'Mr. B', hours: 18, maxHours: 30 },
  { name: 'Ms. C', hours: 28, maxHours: 30 },
  { name: 'Mr. D', hours: 15, maxHours: 30 },
  { name: 'Ms. E', hours: 22, maxHours: 30 },
];

const roomUtilizationData = [
  { name: 'Room 101', hours: 30, capacity: 40 },
  { name: 'Lab 1', hours: 20, capacity: 40 },
  { name: 'Room 202', hours: 35, capacity: 40 },
  { name: 'Hall A', hours: 10, capacity: 40 },
];

const disruptionTrendData = [
  { month: 'Jan', absences: 5 },
  { month: 'Feb', absences: 8 },
  { month: 'Mar', absences: 3 },
  { month: 'Apr', absences: 7 },
  { month: 'May', absences: 6 },
];

const nepComplianceData = [
  { name: 'Foundational', value: 95, fill: 'var(--color-foundational)' },
  { name: 'Preparatory', value: 90, fill: 'var(--color-preparatory)' },
  { name: 'Middle', value: 85, fill: 'var(--color-middle)' },
  { name: 'Secondary', value: 92, fill: 'var(--color-secondary)' },
];
const chartConfigCompliance = {
  foundational: { label: 'Foundational', color: 'hsl(var(--chart-1))' },
  preparatory: { label: 'Preparatory', color: 'hsl(var(--chart-2))' },
  middle: { label: 'Middle', color: 'hsl(var(--chart-3))' },
  secondary: { label: 'Secondary', color: 'hsl(var(--chart-4))' },
};


const chartConfigUtilization = {
  hours: { label: "Actual Hours", color: "hsl(var(--chart-1))" },
  maxHours: { label: "Max Hours", color: "hsl(var(--chart-2))" },
};
const chartConfigAbsences = {
  absences: { label: "Absences", color: "hsl(var(--destructive))" },
};


const StatCard = ({ title, value, icon: Icon, description }: { title: string, value: string, icon: React.ElementType, description: string }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-xs text-muted-foreground">{description}</p>
    </CardContent>
  </Card>
);

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-headline text-2xl">Analytics Dashboard</CardTitle>
          <CardDescription>
            Visualize resource utilization, disruption trends, and NEP 2020 compliance.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Teachers" value="45" icon={Users} description="+2 this month" />
        <StatCard title="Total Classrooms" value="20" icon={BookOpen} description="1 new lab added" />
        <StatCard title="Avg. Disruptions/Week" value="3.5" icon={AlertTriangle} description="-0.5 from last week" />
        <StatCard title="Overall Compliance" value="91%" icon={CheckSquare} description="NEP 2020 guidelines" />
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Teacher Utilization</CardTitle>
          </CardHeader>
          <CardContent>
             <ChartContainer config={chartConfigUtilization} className="h-[300px] w-full">
              <BarChart data={teacherUtilizationData} accessibilityLayer>
                <XAxis dataKey="name" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend content={<ChartLegend content={<ChartLegendContent />} />} />
                <Bar dataKey="hours" fill="var(--color-hours)" radius={4} />
                <Bar dataKey="maxHours" fill="var(--color-maxHours)" radius={4} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Classroom Utilization</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfigUtilization} className="h-[300px] w-full">
              <BarChart data={roomUtilizationData} accessibilityLayer>
                <XAxis dataKey="name" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend content={<ChartLegend content={<ChartLegendContent />} />} />
                <Bar dataKey="hours" fill="var(--color-hours)" radius={4} />
                 {/* Could add capacity as another bar or line */}
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-headline">Disruption Trends (Absences)</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfigAbsences} className="h-[300px] w-full">
              <LineChart data={disruptionTrendData} accessibilityLayer margin={{ left: 12, right: 12 }}>
                <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8}/>
                <YAxis tickMargin={8} />
                <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
                <Line type="monotone" dataKey="absences" stroke="var(--color-absences)" strokeWidth={2} dot={false} />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-headline">NEP 2020 Compliance by Stage</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <ChartContainer config={chartConfigCompliance} className="h-[300px] w-full max-w-[400px]">
              <PieChart accessibilityLayer>
                <ChartTooltip content={<ChartTooltipContent nameKey="name" hideLabel />} />
                <Pie data={nepComplianceData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label >
                   {nepComplianceData.map((entry) => (
                    <Cell key={`cell-${entry.name}`} fill={entry.fill} />
                  ))}
                </Pie>
                 <ChartLegend content={<ChartLegendContent nameKey="name" />} className="-translate-y-2 flex-wrap gap-2 [&>*]:basis-1/4 [&>*]:justify-center" />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>
       <Card>
        <CardHeader>
          <CardTitle className="font-headline">More Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Detailed reports on subject coverage, teacher workload balance, and more can be generated here. Export options (PDF/Excel) will be available.</p>
        </CardContent>
      </Card>
    </div>
  );
}
