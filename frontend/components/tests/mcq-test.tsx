"use client";

import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Lock, Brain } from "lucide-react";

export function MCQTest() {
  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="text-3xl font-heading font-bold text-dark">MCQ Test</h1>
          <p className="text-dark/60 mt-1 font-body">Knowledge assessment for your eating habits</p>
        </div>
      </motion.div>

      {/* Locked State */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className="p-12 text-center bg-dark/5">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-dark/10 mb-6">
            <Lock className="w-10 h-10 text-dark/50" />
          </div>

          <h2 className="text-2xl font-heading font-bold text-dark mb-2">Test Locked</h2>
          <p className="text-dark/60 font-body mb-6 max-w-md mx-auto">
            Complete the 7-day challenge with <strong>85%+ compliance</strong> to unlock this test and earn your qualification badge.
          </p>

          <div className="space-y-4 max-w-md mx-auto">
            <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <p className="text-sm font-semibold text-primary mb-2 flex items-center gap-2">
                <Brain className="w-4 h-4" />
                What This Test Measures
              </p>
              <ul className="text-sm text-dark/70 font-body space-y-1">
                <li>• Your understanding of nutrition basics</li>
                <li>• Knowledge of healthy eating patterns</li>
                <li>• Awareness of portion control</li>
                <li>• Food grouping and balance</li>
              </ul>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-semibold text-blue-900 mb-1">📊 Current Status</p>
              <p className="text-sm text-blue-800 font-body">
                Go back to the <strong>7-Day Challenge</strong> to log your meals and reach 85% compliance.
              </p>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
