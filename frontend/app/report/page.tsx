"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getReport, type ChallengeReport } from "@/lib/api";
import { Loader2, Trophy, Star, TrendingUp, Lightbulb, Leaf, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const CLIENT_ID_KEY = "sarvarasa_client_id";

const PATTERN_LABELS: Record<string, string> = {
  PROTEIN_PRESENT:   "Protein",
  VEGETABLE_PRESENT: "Vegetables",
  FRUIT_PRESENT:     "Fruits",
  FIBER_SOURCE:      "Fibre",
  TRADITIONAL_FOOD:  "Traditional Foods",
  BALANCED_MEAL:     "Balanced Meals",
  PROCESSED_FOOD:    "Processed Food",
  SUGARY_BEVERAGE:   "Sugary Drinks",
};

function PatternBar({ label, pct, isGood }: { label: string; pct: number; isGood: boolean }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs font-body">
        <span className="text-dark/70">{label}</span>
        <span className={cn("font-semibold", isGood ? "text-accent" : "text-primary")}>{pct}%</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={cn("h-full rounded-full", isGood ? "bg-accent" : "bg-primary")}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export default function ReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<ChallengeReport | null>(null);
  const [loading, setLoading] = useState(true);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) { router.push("/onboarding"); return; }
    getReport(clientId)
      .then(setReport)
      .catch(() => router.push("/challenge/progress"))
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

  if (!report) return null;

  const qualStatus = report.qualification_status;
  const isQualified = qualStatus === "QUALIFIED";
  const isSecondChance = qualStatus === "SECOND_CHANCE";
  const isLocked = qualStatus === "LOCKED";

  const goodPatterns = ["PROTEIN_PRESENT", "VEGETABLE_PRESENT", "FRUIT_PRESENT", "FIBER_SOURCE", "TRADITIONAL_FOOD", "BALANCED_MEAL"];
  const badPatterns = ["PROCESSED_FOOD", "SUGARY_BEVERAGE"];

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <Leaf className="w-6 h-6 text-primary" />
            <span className="font-body text-sm text-dark/50 uppercase tracking-widest">Sarvarasa</span>
          </div>
          <h1 className="font-heading text-3xl font-bold text-dark">Your Food Awareness Report</h1>
          <p className="font-body text-dark/60 mt-1">
            {report.client_name} · {report.completed_days} days completed · {report.compliance_score}% compliance
          </p>
        </motion.div>

        {/* Qualification Status */}
        <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.05 }}>
          <Card className={cn(
            "border-2",
            isQualified ? "border-accent/40 bg-accent/5" :
            isSecondChance ? "border-primary/30 bg-primary/5" :
            "border-destructive/30 bg-destructive/5"
          )}>
            <CardContent className="p-6 text-center">
              <div className={cn(
                "w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4",
                isQualified ? "bg-accent/10" : "bg-primary/10"
              )}>
                <Trophy className={cn("w-8 h-8", isQualified ? "text-accent" : "text-primary")} />
              </div>
              <Badge className={cn(
                "mb-3 text-sm px-3 py-1",
                isQualified ? "bg-accent/20 text-accent border-accent/30" :
                isSecondChance ? "bg-primary/20 text-primary border-primary/30" :
                "bg-destructive/20 text-destructive border-destructive/30"
              )}>
                {isQualified ? "QUALIFIED" : isSecondChance ? "SECOND CHANCE" : "LOCKED"}
              </Badge>
              <h2 className="font-heading text-xl font-semibold text-dark mb-2">
                {isQualified
                  ? "Congratulations! You've qualified."
                  : isSecondChance
                  ? "Almost there — one more week!"
                  : "Challenge locked."}
              </h2>
              <p className="font-body text-sm text-dark/60">
                {isQualified
                  ? "You completed the 7-Day Wholesome Eating Challenge and unlocked your report."
                  : isSecondChance
                  ? "You get a free second week. Complete 6+ more days with all 3 meals to qualify."
                  : "Reactivate for ₹299 to try again with a fresh challenge cycle."}
              </p>
              {isSecondChance && (
                <Link href="/challenge" className="mt-4 inline-block">
                  <Button>Start Week 2 <ArrowRight className="w-4 h-4 ml-2" /></Button>
                </Link>
              )}
              {isLocked && (
                <Link href="/reactivate" className="mt-4 inline-block">
                  <Button variant="destructive">Reactivate — ₹299</Button>
                </Link>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Food Pattern Analysis */}
        {Object.keys(report.food_pattern_summary || {}).length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <span>🔍</span> Your Food Patterns
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="font-body text-xs text-dark/50 mb-4">
                  Based on {report.food_pattern_summary ? "your" : ""} meal descriptions across the 7 days.
                </p>
                {goodPatterns.map((key) => {
                  const pct = (report.food_pattern_summary as Record<string, number>)[key];
                  if (pct === undefined) return null;
                  return <PatternBar key={key} label={PATTERN_LABELS[key] || key} pct={pct} isGood />;
                })}
                <div className="border-t border-border/50 pt-3 mt-3">
                  {badPatterns.map((key) => {
                    const pct = (report.food_pattern_summary as Record<string, number>)[key];
                    if (pct === undefined) return null;
                    return <PatternBar key={key} label={PATTERN_LABELS[key] || key} pct={pct} isGood={false} />;
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Observations */}
        {report.food_observations?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Lightbulb className="w-4 h-4 text-primary" /> Food Habit Observations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {report.food_observations.map((obs, i) => (
                  <div key={i} className="flex gap-3 p-3 bg-muted/50 rounded-xl">
                    <span className="text-lg shrink-0">💬</span>
                    <p className="font-body text-sm text-dark/80 leading-relaxed">{obs}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Strengths */}
        {report.strengths?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Star className="w-4 h-4 text-accent" /> Your Strengths
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {report.strengths.map((s, i) => (
                  <div key={i} className="flex gap-2 items-start">
                    <span className="text-accent mt-0.5">✓</span>
                    <p className="font-body text-sm text-dark/80">{s}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Improvement Areas */}
        {report.improvement_areas?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="w-4 h-4 text-primary" /> Improvement Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {report.improvement_areas.map((item, i) => (
                  <div key={i} className="flex gap-2 items-start">
                    <span className="text-primary mt-0.5">→</span>
                    <p className="font-body text-sm text-dark/80">{item}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Action Plan */}
        {report.action_plan?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card className="border-primary/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Your Action Plan</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {report.action_plan.map((step, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <p className="font-body text-sm text-dark/80 leading-relaxed">{step}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Wholesome Plate Education */}
        {report.wholesome_plate_tips?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <Card className="bg-accent/5 border-accent/20">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <span>🌿</span> The Wholesome Plate
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {report.wholesome_plate_tips.map((tip, i) => (
                  <div key={i} className="flex gap-2 items-start">
                    <Leaf className="w-4 h-4 text-accent shrink-0 mt-0.5" />
                    <p className="font-body text-sm text-dark/70">{tip}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}

        <p className="font-body text-xs text-center text-dark/30 pb-4">
          Sarvarasa · Food awareness through observation, not restriction.
        </p>
      </div>
    </AppShell>
  );
}
