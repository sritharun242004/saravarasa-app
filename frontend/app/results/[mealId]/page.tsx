"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import Image from "next/image";
import { AppShell } from "@/components/layout/app-shell";
import { NutritionCard } from "@/components/analysis/nutrition-card";
import { HealthScores } from "@/components/analysis/health-scores";
import { MicronutrientsCard } from "@/components/analysis/micronutrients-card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getMeal, type NutritionResult } from "@/lib/api";
import { Camera, Share2, ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { toast } from "@/lib/use-toast";

export default function ResultsPage() {
  const params = useParams();
  const mealId = params.mealId as string;
  const [meal, setMeal] = useState<NutritionResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMeal(mealId)
      .then(setMeal)
      .catch(() => toast({ title: "Failed to load results", variant: "destructive" }))
      .finally(() => setLoading(false));
  }, [mealId]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
            <p className="font-body text-dark/60">Loading your results...</p>
          </div>
        </div>
      </AppShell>
    );
  }

  if (!meal) return null;

  const handleShare = async () => {
    try {
      await navigator.share({
        title: "My NutriLens Analysis",
        text: `I just analyzed my ${meal.foods.join(", ")} — ${Math.round(meal.total_calories)} calories with NutriLens India!`,
      });
    } catch {
      toast({ title: "Copied to clipboard", description: "Share link copied!" });
    }
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <div className="flex items-center justify-between">
          <Link href="/analyze">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4" />
              New Meal
            </Button>
          </Link>
          <Button variant="ghost" size="sm" onClick={handleShare}>
            <Share2 className="w-4 h-4" />
            Share
          </Button>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {meal.image_url && (
            <div className="relative rounded-3xl overflow-hidden aspect-[4/3] bg-muted mb-4">
              <Image src={meal.image_url} alt="Analyzed meal" fill className="object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-dark/40 to-transparent" />
              <div className="absolute bottom-4 left-4 right-4">
                <h1 className="font-heading text-xl font-bold text-white">
                  {meal.foods.join(", ")}
                </h1>
                <p className="font-body text-white/70 text-sm mt-1">
                  {new Date(meal.created_at).toLocaleDateString("en-IN", {
                    day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"
                  })}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 flex-wrap mb-6">
            {meal.foods.map((food) => (
              <Badge key={food} variant="default">{food}</Badge>
            ))}
          </div>
        </motion.div>

        <NutritionCard meal={meal} />
        <HealthScores scores={meal.health_scores} />
        <MicronutrientsCard micronutrients={meal.micronutrients} />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex gap-3 pb-4"
        >
          <Link href="/analyze" className="flex-1">
            <Button variant="outline" size="lg" className="w-full">
              <Camera className="w-4 h-4" />
              Analyze Another
            </Button>
          </Link>
          <Link href="/history" className="flex-1">
            <Button size="lg" className="w-full">
              View History
            </Button>
          </Link>
        </motion.div>
      </div>
    </AppShell>
  );
}
