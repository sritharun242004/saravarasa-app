"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Lock, Loader2, AlertCircle, CheckCircle, TrendingUp } from "lucide-react";

interface DayProgress {
  day: number;
  meals_logged: number;
  total_meals: number;
  completed: boolean;
  submitted_at?: string;
}

interface ChallengeState {
  days: DayProgress[];
  compliance_pct: number;
  status: "in_progress" | "completed" | "failed";
  passed: boolean;
  started_at: string;
  ended_at?: string;
}

export function ChallengeTracker() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [challengeState, setChallengeState] = useState<ChallengeState | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadChallengeState();
  }, []);

  const loadChallengeState = async () => {
    try {
      const clientId = localStorage.getItem("clientId");
      const token = localStorage.getItem("authToken");

      if (!clientId) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/challenge/${clientId}/progress`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error("Failed to load challenge");

      const data = await response.json();
      setChallengeState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-body">{error}</p>
        </div>
      </div>
    );
  }

  if (!challengeState) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-dark/30 mx-auto mb-4" />
          <p className="text-dark/60 font-body">No challenge started yet</p>
          <Button onClick={() => loadChallengeState()} className="mt-4">
            Refresh
          </Button>
        </div>
      </div>
    );
  }

  const passed = challengeState.compliance_pct >= 85;
  const daysLeft = 7 - challengeState.days.filter((d) => d.completed).length;

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="text-3xl font-heading font-bold text-dark">7-Day Challenge</h1>
          <p className="text-dark/60 mt-1 font-body">Track your daily meals and build consistency</p>
        </div>
      </motion.div>

      {/* Compliance Score Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className="p-6 bg-gradient-to-br from-primary/10 to-secondary/10 border-primary/20">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-sm text-dark/60 font-body uppercase tracking-wide mb-2">Compliance Score</p>
              <div className="flex items-baseline gap-3">
                <div className="text-5xl font-heading font-bold text-dark">
                  {Math.round(challengeState.compliance_pct)}%
                </div>
                <div className="text-lg text-dark/60 font-body">/ 100%</div>
              </div>
            </div>

            <motion.div
              animate={{ scale: passed ? [1, 1.1, 1] : 1 }}
              transition={{ repeat: passed ? Infinity : 0, duration: 2 }}
              className={`w-16 h-16 rounded-full flex items-center justify-center ${
                passed ? "bg-primary/20" : "bg-dark/10"
              }`}
            >
              {passed ? (
                <CheckCircle className="w-10 h-10 text-primary" />
              ) : (
                <TrendingUp className="w-10 h-10 text-dark/40" />
              )}
            </motion.div>
          </div>

          {/* Threshold Indicator */}
          <div className="space-y-2">
            <div className="h-2 bg-dark/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(challengeState.compliance_pct, 100)}%` }}
                transition={{ duration: 1, delay: 0.2 }}
                className="h-full bg-primary"
              />
            </div>
            <div className="flex justify-between text-xs font-body text-dark/60">
              <span>0%</span>
              <span className="font-semibold text-primary">85% Required to Pass</span>
              <span>100%</span>
            </div>
          </div>

          {/* Status Badge */}
          <div className="mt-6 p-3 rounded-lg bg-white/50">
            {passed ? (
              <p className="text-sm font-body text-primary font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                ✨ You've qualified! Unlock exclusive doctor consultation discounts.
              </p>
            ) : (
              <p className="text-sm font-body text-dark/70 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {daysLeft} days left to reach 85% compliance
              </p>
            )}
          </div>
        </Card>
      </motion.div>

      {/* 7-Day Grid */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <div>
          <h2 className="text-lg font-heading font-bold text-dark mb-4">Daily Progress</h2>
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }, (_, i) => i + 1).map((day) => {
              const dayProgress = challengeState.days.find((d) => d.day === day);
              const completed = dayProgress?.completed ?? false;
              const mealsLogged = dayProgress?.meals_logged ?? 0;

              return (
                <Link key={day} href={`/app/challenge/day/${day}`}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: day * 0.05 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="group"
                  >
                    <Card
                      className={`p-3 text-center cursor-pointer transition-all ${
                        completed
                          ? "bg-primary/20 border-primary/50"
                          : "bg-white hover:bg-dark/5"
                      }`}
                    >
                      <div className="flex items-center justify-center mb-2">
                        {completed ? (
                          <CheckCircle2 className="w-6 h-6 text-primary" />
                        ) : (
                          <Circle className="w-6 h-6 text-dark/30 group-hover:text-dark/50" />
                        )}
                      </div>
                      <p className="text-xs font-heading font-bold text-dark mb-1">Day {day}</p>
                      <p className="text-xs font-body text-dark/60">
                        {mealsLogged}/{3} meals
                      </p>
                    </Card>
                  </motion.div>
                </Link>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <div className="flex gap-4">
          <Link href={`/app/challenge/day/1`} className="flex-1">
            <Button className="w-full bg-primary hover:bg-primary/90">
              Continue Challenge →
            </Button>
          </Link>
          {challengeState.status === "completed" && (
            <Link href="/app/results" className="flex-1">
              <Button variant="outline" className="w-full">
                View Results
              </Button>
            </Link>
          )}
        </div>
      </motion.div>

      {/* Info Box */}
      {!passed && challengeState.compliance_pct > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <p className="text-sm font-body text-blue-900">
            💡 <strong>Tip:</strong> Log all your meals (breakfast, lunch, dinner) every day to maintain consistency and hit the 85% threshold.
          </p>
        </motion.div>
      )}
    </div>
  );
}
