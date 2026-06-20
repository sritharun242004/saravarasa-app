"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { getChallengeProgress, type ChallengeProgress } from "@/lib/api";
import { Loader2, CheckCircle2, Circle, Lock, ArrowRight, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

const CLIENT_ID_KEY = "sarvarasa_client_id";

const MEAL_ICONS: Record<string, string> = {
  BREAKFAST: "🌅",
  LUNCH: "☀️",
  DINNER: "🌙",
  SNACK: "🍎",
};

function DayCard({ day, completedDays, currentDay }: { day: number; completedDays: number[]; currentDay: number }) {
  const isComplete = completedDays.includes(day);
  const isCurrent = day === currentDay;
  const isFuture = day > currentDay;
  const isPast = day < currentDay;

  const cardContent = (
    <motion.div
      whileHover={{ scale: isFuture ? 1 : 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "rounded-2xl border p-4 transition-all duration-200",
        isComplete ? "border-accent/40 bg-accent/5 cursor-pointer" :
        isCurrent ? "border-primary/40 bg-primary/5 ring-1 ring-primary/20 cursor-pointer" :
        isFuture ? "border-border/50 bg-card opacity-40 cursor-not-allowed" :
        "border-border bg-card opacity-70 cursor-pointer"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-heading text-sm font-semibold text-dark/60">Day {day}</span>
        {isComplete ? (
          <CheckCircle2 className="w-5 h-5 text-accent" />
        ) : isCurrent ? (
          <Circle className="w-5 h-5 text-primary animate-pulse" />
        ) : isFuture ? (
          <Lock className="w-4 h-4 text-dark/30" />
        ) : (
          <CheckCircle2 className="w-5 h-5 text-dark/30 opacity-50" />
        )}
      </div>
      <div className="flex gap-1.5 mt-2">
        {["BREAKFAST", "LUNCH", "DINNER"].map((meal) => (
          <div
            key={meal}
            className={cn(
              "flex-1 h-1.5 rounded-full",
              isComplete ? "bg-accent" : isCurrent ? "bg-primary/30" : "bg-muted"
            )}
          />
        ))}
      </div>
      {isCurrent && (
        <p className="font-body text-xs text-primary font-medium mt-2">📝 Log today's meals →</p>
      )}
      {isPast && !isComplete && (
        <p className="font-body text-xs text-dark/40 mt-2">Day passed (no submission)</p>
      )}
      {isFuture && (
        <p className="font-body text-xs text-dark/30 mt-2">Coming soon</p>
      )}
    </motion.div>
  );

  // Only make current and past days clickable
  if (isFuture) {
    return cardContent;
  }

  return <Link href={`/challenge/day/${day}`}>{cardContent}</Link>;
}

export default function ChallengePage() {
  const router = useRouter();
  const [progress, setProgress] = useState<ChallengeProgress | null>(null);
  const [loading, setLoading] = useState(true);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) {
      router.push("/onboarding");
      return;
    }
    getChallengeProgress(clientId)
      .then(setProgress)
      .catch(() => router.push("/audit"))
      .finally(() => setLoading(false));
  }, [clientId, router]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (!progress) return null;

  const completedDays = progress.days_detail
    ? Object.entries(progress.days_detail)
        .filter(([, types]) => ["BREAKFAST", "LUNCH", "DINNER"].every((t) => (types as string[]).includes(t)))
        .map(([d]) => parseInt(d))
    : [];

  // Use backend's current_day to enforce day-by-day restrictions
  const currentDay = progress.current_day || 1;
  const compliancePct = progress.compliance_pct || 0;
  const consistencyPct = progress.consistency_pct || 0;

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="font-heading text-3xl font-bold text-dark">7-Day Challenge</h1>
          <p className="font-body text-dark/60 mt-1">
            {progress.client_name} · Cycle {progress.challenge_cycle || 1}
          </p>
        </motion.div>

        {/* Compliance Card */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-body text-sm text-dark/60">Compliance</p>
                  <p className="font-heading text-4xl font-bold text-primary">
                    {compliancePct}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-body text-sm text-dark/60">Days Complete</p>
                  <p className="font-heading text-2xl font-bold text-dark">
                    {completedDays.length} <span className="text-dark/40 text-lg">/ 7</span>
                  </p>
                </div>
              </div>
              <Progress value={compliancePct} className="h-2.5" />
              <div className="flex items-center justify-between mt-2">
                <p className="font-body text-xs text-dark/50">Target: 85%+ to qualify</p>
                {compliancePct >= 85 && (
                  <span className="font-body text-xs font-semibold text-accent">On Track ✓</span>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Consistency Card */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.07 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-body text-sm text-dark/60">Consistency</p>
                  <p className="font-heading text-4xl font-bold text-secondary">
                    {consistencyPct}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-body text-sm text-dark/60">Current Day</p>
                  <p className="font-heading text-2xl font-bold text-dark">
                    <span className="text-primary">{currentDay}</span> <span className="text-dark/40 text-lg">/ 7</span>
                  </p>
                </div>
              </div>
              <Progress value={consistencyPct} className="h-2.5" />
              <div className="mt-2">
                <p className="font-body text-xs text-dark/50">
                  {completedDays.length > 0
                    ? `${completedDays.length} day${completedDays.length !== 1 ? 's' : ''} with all 3 meals submitted`
                    : "Start by submitting today's meals"}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Day Grid */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div className="flex items-center gap-2 mb-3">
            <Calendar className="w-4 h-4 text-primary" />
            <h2 className="font-heading text-lg font-semibold text-dark">Your 7 Days</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[1, 2, 3, 4, 5, 6, 7].map((day) => (
              <DayCard key={day} day={day} completedDays={completedDays} currentDay={currentDay} />
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Link href={`/challenge/day/${currentDay}`}>
            <Button size="lg" className="w-full group">
              Log Day {currentDay} Meals
              <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </motion.div>

        {/* Info */}
        <Card className="bg-muted/50 border-border/50">
          <CardContent className="p-4">
            <p className="font-body text-sm text-dark/60 leading-relaxed">
              <span className="font-semibold text-dark">Reminder:</span> Every day requires Breakfast, Lunch, and Dinner
              — each with an image and description. Snack is optional.
              Complete 6 out of 7 days to qualify for your report.
            </p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
