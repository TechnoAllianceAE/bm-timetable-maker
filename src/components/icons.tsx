import type { SVGProps } from 'react';

export const Logo = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 200 50"
    width="120"
    height="30"
    role="img"
    aria-label="K12 Timetable Ace Logo"
    {...props}
  >
    <rect width="200" height="50" rx="5" fill="transparent" />
    <text
      x="10"
      y="35"
      fontFamily="Space Grotesk, sans-serif"
      fontSize="28"
      fontWeight="bold"
      fill="currentColor"
    >
      K12<tspan fill="hsl(var(--accent))">Ace</tspan>
    </text>
  </svg>
);

export const IconPlaceholder = (props: SVGProps<SVGSVGElement>) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    {...props}
  >
    <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
  </svg>
);
