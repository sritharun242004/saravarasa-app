"use client";

import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Lock, PenTool } from "lucide-react";

export function DescriptiveTest() {
  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="text-3xl font-heading font-bold text-dark">Descriptive Test</h1>
          <p className="text-dark/60 mt-1 font-body">Personal insights and recommendations</p>
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
            This test unlocks after you complete and pass the <strong>MCQ Test</strong>. It provides personalized feedback based on your eating patterns.
          </p>

          <div className="space-y-4 max-w-md mx-auto">
            <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <p className="text-sm font-semibold text-primary mb-2 flex items-center gap-2">
                <PenTool className="w-4 h-4" />
                What You'll Receive
              </p>
              <ul className="text-sm text-dark/70 font-body space-y-1">
                <li>• Personalized meal recommendations</li>
                <li>• Your nutrition pattern analysis</li>
                <li>• Areas for improvement</li>
                <li>• Long-term lifestyle suggestions</li>
              </ul>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm font-semibold text-green-900 mb-1">✅ Unlock Path</p>
              <p className="text-sm text-green-800 font-body">
                1. Log 7 days of meals<br/>
                2. Reach 85%+ compliance<br/>
                3. Pass the MCQ Test<br/>
                4. This test unlocks automatically
              </p>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
