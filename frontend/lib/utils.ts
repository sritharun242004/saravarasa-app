import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCalories(cal: number): string {
  return Math.round(cal).toLocaleString("en-IN");
}

export function formatNutrient(value: number, unit: string): string {
  return `${value.toFixed(1)}${unit}`;
}

// Parsed as local midnight (not UTC) so a "YYYY-MM-DD" date never shifts by a day.
export function formatDayDate(iso?: string | null): string | null {
  if (!iso) return null;
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

// Stored/sent to the backend as 24-hour "HH:MM"; only formatted as 12-hour for display.
export function formatTime12(time24?: string | null): string | null {
  if (!time24) return null;
  const [hhStr, mm] = time24.split(":");
  let h = parseInt(hhStr, 10);
  if (isNaN(h) || !mm) return time24;
  const period = h >= 12 ? "PM" : "AM";
  h = h % 12 || 12;
  return `${String(h).padStart(2, "0")}:${mm} ${period}`;
}

export function getHealthScoreColor(score: number): string {
  if (score >= 75) return "#22C55E";
  if (score >= 50) return "#1B6040";
  if (score >= 25) return "#1B3020";
  return "#DC2626";
}

export function getHealthScoreLabel(score: number): string {
  if (score >= 75) return "Excellent";
  if (score >= 50) return "Good";
  if (score >= 25) return "Fair";
  return "Poor";
}
