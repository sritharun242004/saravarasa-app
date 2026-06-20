"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { getChallengeProgress, generateReport, type ChallengeProgress } from "@/lib/api";
import { Loader2, CheckCircle2, XCircle, Clock, ArrowRight, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

const CLIENT_ID_KEY = "sarvarasa_client_id";

export default function ProgressPage() {
  const router = useRouter();
  const [progress, setProgress] = useState<ChallengeProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) { router.push("/onboarding"); return; }
    getChallengeProgress(clientId)
      .then(setProgress)
      .finally(() => setLoading(false));
  }, [clientId, router]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      await generateReport(clientId);
      router.push("/report");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Could not generate report. Ensure 6+ days are complete.";
      alert(msg);
    } finally {
      setGenerating(false);
    }
  };

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

  const compliancePct = progress.compliance_pct || 0;
  const completedDays = progress.completed_days || 0;
  const isQualified = compliancePct >= 85;
  const daysDetail = progress.days_detail || {};

  const REQUIRED_MEALS = ["BREAKFAST", "LUNCH", "DINNER"];

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="font-heading text-3xl font-bold text-dark">Challenge Progress</h1>
          <p className="font-body text-dark/60 mt-1">{progress.client_name}</p>
        </motion.div>

        {/* Main Compliance Card */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card className={cn(
            "border-2",
            isQualified ? "border-accent/30 bg-accent/5" : "border-primary/20"
          )}>
            <CardContent className="p-6">
              <div className="flex items-center gap-4 mb-5">
                <div className={cn(
                  "w-14 h-14 rounded-2xl flex items-center justify-center",
                  isQualified ? "bg-accent/10" : "bg-primary/10"
                )}>
                  {isQualified ? (
                    <Trophy className="w-7 h-7 text-accent" />
                  ) : (
                    <Clock className="w-7 h-7 text-primary" />
                  )}
                </div>
                <div>
                  <p className="font-heading text-4xl font-bold text-dark">{compliancePct}%</p>
                  <p className="font-body text-sm text-dark/60">
                    {completedDays} of 7 days complete
                  </p>
                </div>
              </div>
              <Progress value={compliancePct} className="h-3 mb-3" />
              <div className="flex justify-between text-xs font-body">
                <span className="text-dark/50">0%</span>
                <span className={cn("font-semibold", isQualified ? "text-accent" : "text-primary")}>
                  {isQualified ? "QUALIFIED ✓" : `Need ${Math.max(0, 85 - compliancePct).toFixed(1)}% more`}
                </span>
                <span className="text-dark/50">85%+</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Day-by-Day Breakdown */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Day-by-Day Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[1, 2, 3, 4, 5, 6, 7].map((day) => {
                const submitted = (daysDetail[day.toString()] || []) as string[];
                const requiredDone = REQUIRED_MEALS.every((t) => submitted.includes(t));
                const partialDone = submitted.length > 0;

                return (
                  <Link key={day} href={`/challenge/day/${day}`}>
                    <div className={cn(
                      "flex items-center gap-3 p-3 rounded-xl border transition-colors hover:bg-muted/50",
                      requiredDone ? "border-accent/20 bg-accent/5" : "border-border"
                    )}>
                      {requiredDone ? (
                        <CheckCircle2 className="w-5 h-5 text-accent shrink-0" />
                      ) : partialDone ? (
                        <div className="w-5 h-5 rounded-full border-2 border-primary/40 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-dark/20 shrink-0" />
                      )}
                      <span className="font-body text-sm font-medium text-dark">Day {day}</span>
                      <div className="flex gap-1 ml-auto">
                        {REQUIRED_MEALS.map((meal) => (
                          <div
                            key={meal}
                            className={cn(
                              "w-2 h-2 rounded-full",
                              submitted.includes(meal) ? "bg-accent" : "bg-muted"
                            )}
                            title={meal}
                          />
                        ))}
                      </div>
                      {!requiredDone && (
                        <ArrowRight className="w-4 h-4 text-dark/30 ml-1" />
                      )}
                    </div>
                  </Link>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* Report Generation */}
        {isQualified && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15 }}
          >
            <Card className="border-accent/30 bg-accent/5">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Trophy className="w-6 h-6 text-accent" />
                </div>
                <h3 className="font-heading text-xl font-semibold text-dark mb-2">
                  You&apos;ve Qualified!
                </h3>
                <p className="font-body text-sm text-dark/60 mb-5">
                  You completed {completedDays} days with {compliancePct}% compliance.
                  Your personalized food awareness report is ready.
                </p>
                <Button onClick={handleGenerateReport} disabled={generating} className="w-full">
                  {generating ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Generating…</>
                  ) : (
                    <>View My Report <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {!isQualified && completedDays < 7 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Link href={`/challenge/day/${completedDays + 1}`}>
              <Button size="lg" className="w-full group">
                Continue Day {completedDays + 1}
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
