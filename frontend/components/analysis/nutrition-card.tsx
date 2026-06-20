"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { NutritionResult } from "@/lib/api";

interface Props {
  meal: NutritionResult;
}

const DAILY_TARGETS = {
  calories: 2000,
  protein: 50,
  carbs: 275,
  fat: 78,
  fiber: 28,
};

export function NutritionCard({ meal }: Props) {
  const macros = [
    {
      label: "Calories",
      value: Math.round(meal.total_calories),
      unit: "kcal",
      daily: DAILY_TARGETS.calories,
      color: "bg-primary",
      highlight: true,
    },
    {
      label: "Protein",
      value: +meal.protein_g.toFixed(1),
      unit: "g",
      daily: DAILY_TARGETS.protein,
      color: "bg-accent",
    },
    {
      label: "Carbohydrates",
      value: +meal.carbs_g.toFixed(1),
      unit: "g",
      daily: DAILY_TARGETS.carbs,
      color: "bg-secondary",
    },
    {
      label: "Fat",
      value: +meal.fat_g.toFixed(1),
      unit: "g",
      daily: DAILY_TARGETS.fat,
      color: "bg-primary-300",
    },
    {
      label: "Fiber",
      value: +meal.fiber_g.toFixed(1),
      unit: "g",
      daily: DAILY_TARGETS.fiber,
      color: "bg-accent-300",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Nutrition Breakdown</CardTitle>
          <p className="font-body text-sm text-dark/60">% of daily recommended intake</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {macros.map((macro) => {
            const pct = Math.min(Math.round((macro.value / macro.daily) * 100), 100);
            return (
              <div key={macro.label}>
                <div className="flex justify-between items-end mb-2">
                  <span className="font-body font-semibold text-dark/80">{macro.label}</span>
                  <span className={`font-heading font-bold ${macro.highlight ? "text-2xl text-primary" : "text-lg text-dark"}`}>
                    {macro.value}
                    <span className="font-body text-sm font-normal text-dark/50 ml-1">{macro.unit}</span>
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Progress value={pct} className="flex-1 h-2.5" />
                  <span className="font-body text-xs text-dark/50 w-10 text-right">{pct}%</span>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </motion.div>
  );
}
