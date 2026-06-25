"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, AlertCircle, CreditCard, Download, Share2, Loader2 } from "lucide-react";

interface Report {
  compliance_score: number;
  eligibility_band: string;
  passed: boolean;
  meal_pattern: string;
  strengths: string[];
  improvement_areas: string[];
  action_plan: string[];
  generated_at: string;
  llm_analysis?: string;
  discount_percentage?: number;
}

export function ReportDisplay() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      const clientId = localStorage.getItem("clientId");
      const token = localStorage.getItem("authToken");

      if (!clientId) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/reports/${clientId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          setError("No report generated yet. Complete the 7-day challenge to generate your report.");
          return;
        }
        throw new Error("Failed to load report");
      }

      const data = await response.json();
      setReport(data);
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
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700 font-body flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  const passed = report.compliance_score >= 85;
  const bandColors: Record<string, string> = {
    gold: "from-yellow-400 to-yellow-600",
    strong: "from-blue-400 to-blue-600",
    moderate: "from-orange-400 to-orange-600",
    not_ready: "from-gray-400 to-gray-600",
  };

  const bandColor = bandColors[report.eligibility_band.toLowerCase()] || bandColors.strong;

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="text-3xl font-heading font-bold text-dark">Your Challenge Report</h1>
          <p className="text-dark/60 mt-1 font-body">
            Generated on {new Date(report.generated_at).toLocaleDateString()}
          </p>
        </div>
      </motion.div>

      {/* Main Score Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className={`p-8 bg-gradient-to-br ${bandColor}`}>
          <div className="text-center text-white">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.3 }}
              className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white/20 mb-6"
            >
              {passed ? (
                <CheckCircle2 className="w-12 h-12" />
              ) : (
                <AlertCircle className="w-12 h-12" />
              )}
            </motion.div>

            <h2 className="text-5xl font-heading font-bold mb-2">{report.compliance_score.toFixed(1)}%</h2>
            <p className="text-xl font-semibold mb-2 capitalize">{report.eligibility_band} Candidate</p>

            {passed ? (
              <div className="space-y-4">
                <p className="text-lg font-semibold">🎉 Congratulations! You Qualified!</p>
                <div className="inline-block px-6 py-2 bg-white text-primary rounded-full font-bold">
                  {report.discount_percentage || 50}% Doctor Consultation Discount
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-base font-semibold">You're Below the 85% Threshold</p>
                <p className="text-sm opacity-90">Consider retaking the challenge with a paid enrollment</p>
              </div>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Discount Card (if qualified) */}
      {passed && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="p-6 bg-green-50 border-2 border-green-300">
            <div className="flex items-start gap-4">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-300">
                <CreditCard className="w-6 h-6 text-green-700" />
              </div>
              <div className="flex-1">
                <h3 className="font-heading font-bold text-green-900 mb-1">Exclusive Discount Unlocked!</h3>
                <p className="text-sm text-green-800 font-body mb-4">
                  You've earned a {report.discount_percentage || 50}% discount on doctor consultations. This exclusive offer is valid for 30 days.
                </p>
                <Button className="bg-green-600 hover:bg-green-700 text-white">
                  Book Doctor Consultation Now
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Meal Pattern Analysis */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card className="p-6">
          <h3 className="text-xl font-heading font-bold text-dark mb-4">Your Meal Pattern: {report.meal_pattern}</h3>
          {report.llm_analysis && (
            <p className="text-dark/70 font-body leading-relaxed">{report.llm_analysis}</p>
          )}
        </Card>
      </motion.div>

      {/* Strengths */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card className="p-6">
          <h3 className="text-lg font-heading font-bold text-dark mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            Your Strengths
          </h3>
          <ul className="space-y-2">
            {report.strengths.map((strength, idx) => (
              <li key={idx} className="flex gap-3 text-dark/70 font-body">
                <span className="text-green-600 font-bold">✓</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </Card>
      </motion.div>

      {/* Areas for Improvement */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
        <Card className="p-6">
          <h3 className="text-lg font-heading font-bold text-dark mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            Areas for Improvement
          </h3>
          <ul className="space-y-2">
            {report.improvement_areas.map((area, idx) => (
              <li key={idx} className="flex gap-3 text-dark/70 font-body">
                <span className="text-orange-600 font-bold">→</span>
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </Card>
      </motion.div>

      {/* Action Plan */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <Card className="p-6 bg-primary/5">
          <h3 className="text-lg font-heading font-bold text-dark mb-4">📋 Your Action Plan</h3>
          <ol className="space-y-3">
            {report.action_plan.map((action, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm">
                  {idx + 1}
                </span>
                <span className="text-dark/70 font-body pt-0.5">{action}</span>
              </li>
            ))}
          </ol>
        </Card>
      </motion.div>

      {/* Action Buttons */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
        <div className="flex gap-4">
          <Button className="bg-primary hover:bg-primary/90 flex-1">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
          <Button variant="outline" className="flex-1">
            <Share2 className="w-4 h-4 mr-2" />
            Share Report
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
