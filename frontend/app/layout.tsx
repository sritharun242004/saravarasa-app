import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

export const metadata: Metadata = {
  title: "Sarvarasa – 7-Day Wholesome Eating Challenge",
  description: "Understand your food habits through simple daily meal tracking and personalized observations. No calorie counting. No meal replacements. Just awareness.",
  keywords: ["wholesome eating", "food habits", "indian food", "7 day challenge", "food awareness", "healthy lifestyle"],
  openGraph: {
    title: "Sarvarasa – 7-Day Wholesome Eating Challenge",
    description: "Discover your food patterns. Build lasting awareness.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#1B6040",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
