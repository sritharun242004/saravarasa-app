"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getHealthScoreColor, getHealthScoreLabel } from "@/lib/utils";

interface Props {
  scores: {
    weight_loss: number;
    muscle_gain: number;
    diabetic_friendly: number;
    heart_health: number;
    overall: number;
  };
}

const scoreCategories = [
  { key: "weight_loss" as const, label: "Weight Loss", icon: "⚖️" },
  { key: "muscle_gain" as const, label: "Muscle Gain", icon: "💪" },
  { key: "diabetic_friendly" as const, label: "Diabetic Friendly", icon: "🩸" },
  { key: "heart_health" as const, label: "Heart Health", icon: "❤️" },
];

function ScoreCircle({ score, size = 80 }: { score: number; size?: number }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = getHealthScoreColor(score);

  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#F5EDE3" strokeWidth="6" />
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="6"
        strokeDasharray={circ}
        strokeDashoffset={circ}
        strokeLinecap="round"
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
      />
    </svg>
  );
}

export function HealthScores({ scores }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Health Scores</CardTitle>
            <div className="text-right">
              <div
                className="font-heading text-3xl font-bold"
                style={{ color: getHealthScoreColor(scores.overall) }}
              >
                {scores.overall}
              </div>
              <div className="font-body text-xs text-dark/50">Overall</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-6">
            {scoreCategories.map(({ key, label, icon }) => {
              const score = scores[key];
              const color = getHealthScoreColor(score);
              return (
                <div key={key} className="flex flex-col items-center gap-2">
                  <div className="relative">
                    <ScoreCircle score={score} size={80} />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="font-heading font-bold text-lg" style={{ color }}>
                        {score}
                      </span>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="font-body text-sm font-medium text-dark">{label}</p>
                    <p className="font-body text-xs" style={{ color }}>
                      {getHealthScoreLabel(score)}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
