"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  micronutrients: {
    calcium_mg: number;
    iron_mg: number;
    vitamin_c_mg: number;
    potassium_mg: number;
    sodium_mg: number;
    vitamin_a_ug: number;
  };
}

const DAILY_LIMITS = {
  calcium_mg: 1000,
  iron_mg: 18,
  vitamin_c_mg: 90,
  potassium_mg: 3500,
  sodium_mg: 2300,
  vitamin_a_ug: 900,
};

const LABELS: Record<string, string> = {
  calcium_mg: "Calcium",
  iron_mg: "Iron",
  vitamin_c_mg: "Vitamin C",
  potassium_mg: "Potassium",
  sodium_mg: "Sodium",
  vitamin_a_ug: "Vitamin A",
};

const UNITS: Record<string, string> = {
  calcium_mg: "mg",
  iron_mg: "mg",
  vitamin_c_mg: "mg",
  potassium_mg: "mg",
  sodium_mg: "mg",
  vitamin_a_ug: "μg",
};

export function MicronutrientsCard({ micronutrients }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Micronutrients</CardTitle>
          <p className="font-body text-sm text-dark/60">Key vitamins & minerals</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(micronutrients).map(([key, value]) => {
              const daily = DAILY_LIMITS[key as keyof typeof DAILY_LIMITS];
              const pct = Math.min(Math.round((value / daily) * 100), 100);
              return (
                <div key={key} className="bg-muted rounded-xl p-4">
                  <p className="font-body text-xs text-dark/50 mb-1">{LABELS[key]}</p>
                  <p className="font-heading text-xl font-bold text-dark">
                    {value.toFixed(1)}
                    <span className="font-body text-xs font-normal text-dark/50 ml-1">{UNITS[key]}</span>
                  </p>
                  <div className="mt-2 h-1 bg-border rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-primary rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.8, delay: 0.5 }}
                    />
                  </div>
                  <p className="font-body text-xs text-dark/40 mt-1">{pct}% daily</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
