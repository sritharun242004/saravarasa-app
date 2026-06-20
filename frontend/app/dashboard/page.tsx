"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { getChallengeProgress, type ChallengeProgress } from "@/lib/api";
import {
  Loader2, ArrowRight, CheckCircle2, Circle, Trophy,
  Leaf, Beef, Apple, Zap, AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

const CLIENT_ID_KEY = "sarvarasa_client_id";

const PATTERN_ICONS: Record<string, { icon: typeof Leaf; color: string; label: string }> = {
  PROTEIN_PRESENT:   { icon: Beef,         color: "text-accent",   label: "Protein" },
  VEGETABLE_PRESENT: { icon: Leaf,         color: "text-accent",   label: "Vegetables" },
  FRUIT_PRESENT:     { icon: Apple,        color: "text-primary",  label: "Fruits" },
  BALANCED_MEAL:     { icon: Trophy,       color: "text-accent",   label: "Balanced Meals" },
  PROCESSED_FOOD:    { icon: AlertCircle,  color: "text-destructive", label: "Processed Foods" },
  SUGARY_BEVERAGE:   { icon: Zap,          color: "text-primary",  label: "Sugary Drinks" },
};

export default function DashboardPage() {
  const router = useRouter();
  const [progress, setProgress] = useState<ChallengeProgress | null>(null);
  const [loading, setLoading] = useState(true);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) { router.push("/onboarding"); return; }
    getChallengeProgress(clientId)
      .then(setProgress)
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

  const completedDays = progress.completed_days || 0;
  const compliancePct = progress.compliance_pct || 0;
  const isQualified = compliancePct >= 85;
  const status = progress.client_status || "ACTIVE";

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="font-heading text-3xl font-bold text-dark">
            Hello, {progress.client_name?.split(" ")[0] || "there"}
          </h1>
          <p className="font-body text-dark/60 mt-1">Your Sarvarasa Challenge dashboard</p>
        </motion.div>

        {/* Status Banner */}
        {status === "QUALIFIED" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-4 bg-accent/10 border border-accent/30 rounded-2xl flex items-center gap-3"
          >
            <Trophy className="w-6 h-6 text-accent shrink-0" />
            <div>
              <p className="font-heading text-sm font-semibold text-dark">Challenge Qualified!</p>
              <p className="font-body text-xs text-dark/60">View your food awareness report.</p>
            </div>
            <Link href="/report" className="ml-auto">
              <Button size="sm">View Report</Button>
            </Link>
          </motion.div>
        )}

        {status === "SECOND_CHANCE" && (
          <div className="p-4 bg-primary/10 border border-primary/20 rounded-2xl">
            <p className="font-heading text-sm font-semibold text-dark mb-1">Second Chance Week</p>
            <p className="font-body text-xs text-dark/60">Complete 6+ more days to qualify.</p>
          </div>
        )}

        {status === "LOCKED" && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-2xl flex items-center justify-between gap-3">
            <div>
              <p className="font-heading text-sm font-semibold text-dark">Challenge Locked</p>
              <p className="font-body text-xs text-dark/60">Reactivate for ₹299 to try again.</p>
            </div>
            <Link href="/reactivate">
              <Button size="sm" variant="destructive">Reactivate</Button>
            </Link>
          </div>
        )}

        {/* Compliance Card */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-body text-sm text-dark/60">7-Day Compliance</p>
                  <p className="font-heading text-4xl font-bold text-primary">{compliancePct}%</p>
                </div>
                <div className="text-right">
                  <p className="font-body text-sm text-dark/60">Days Done</p>
                  <p className="font-heading text-2xl font-bold text-dark">
                    {completedDays}<span className="text-dark/40 text-sm"> / 7</span>
                  </p>
                </div>
              </div>
              <Progress value={compliancePct} className="h-2.5" />
              <p className="font-body text-xs text-dark/40 mt-2">
                {isQualified ? "✓ Qualified — generate your report" : "Need 85%+ compliance (6 days) to qualify"}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Day Status Grid */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Weekly Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2">
                {[1, 2, 3, 4, 5, 6, 7].map((day) => {
                  const submitted = (progress.days_detail?.[day.toString()] || []) as string[];
                  const done = ["BREAKFAST", "LUNCH", "DINNER"].every((t) => submitted.includes(t));
                  const partial = !done && submitted.length > 0;

                  return (
                    <Link key={day} href={`/challenge/day/${day}`}>
                      <div className={cn(
                        "flex flex-col items-center gap-1 p-2 rounded-xl transition-colors",
                        done ? "bg-accent/10" : "hover:bg-muted"
                      )}>
                        <span className="font-body text-xs text-dark/50">D{day}</span>
                        {done ? (
                          <CheckCircle2 className="w-5 h-5 text-accent" />
                        ) : partial ? (
                          <Circle className="w-5 h-5 text-primary/50" />
                        ) : (
                          <Circle className="w-5 h-5 text-dark/20" />
                        )}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="grid grid-cols-2 gap-3"
        >
          <Link href={`/challenge/day/${Math.min(completedDays + 1, 7)}`}>
            <Card className="hover:shadow-card transition-shadow cursor-pointer h-full">
              <CardContent className="p-4">
                <span className="text-2xl mb-2 block">📸</span>
                <p className="font-heading text-sm font-semibold text-dark">Log Today</p>
                <p className="font-body text-xs text-dark/60 mt-0.5">Add meal images + description</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/challenge/progress">
            <Card className="hover:shadow-card transition-shadow cursor-pointer h-full">
              <CardContent className="p-4">
                <span className="text-2xl mb-2 block">📊</span>
                <p className="font-heading text-sm font-semibold text-dark">Full Progress</p>
                <p className="font-body text-xs text-dark/60 mt-0.5">Day-by-day breakdown</p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {isQualified && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Link href="/report">
              <Button size="lg" className="w-full group">
                View My Food Awareness Report
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
