"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getMealHistory, type MealHistory } from "@/lib/api";
import { Search, Camera, ChevronRight, Loader2 } from "lucide-react";

export default function HistoryPage() {
  const [history, setHistory] = useState<MealHistory | null>(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      getMealHistory(page, search)
        .then(setHistory)
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [page, search]);

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <h1 className="font-heading text-3xl font-bold text-dark">Meal History</h1>
          <p className="font-body text-dark/60 mt-1">All your analyzed meals</p>
        </motion.div>

        <div className="relative mb-6">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark/40" />
          <input
            type="text"
            placeholder="Search meals..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-11 pr-4 py-3 bg-card border border-border rounded-2xl font-body text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-6 h-6 text-primary animate-spin" />
          </div>
        ) : !history?.meals.length ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-muted rounded-3xl flex items-center justify-center mx-auto mb-4">
              <Camera className="w-8 h-8 text-dark/30" />
            </div>
            <h3 className="font-heading text-xl font-semibold text-dark mb-2">No meals yet</h3>
            <p className="font-body text-dark/60 mb-6">Start by analyzing your first meal</p>
            <Link href="/analyze">
              <Button>Analyze My First Meal</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {history.meals.map((meal, i) => (
              <motion.div
                key={meal.meal_id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
              >
                <Link href={`/results/${meal.meal_id}`}>
                  <Card className="hover:shadow-card hover:-translate-y-0.5 transition-all duration-200 cursor-pointer">
                    <CardContent className="p-4 flex items-center gap-4">
                      <div className="relative w-20 h-20 rounded-2xl overflow-hidden bg-muted flex-shrink-0">
                        {meal.image_url ? (
                          <Image src={meal.image_url} alt={meal.foods[0]} fill className="object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-2xl">🍛</div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-heading font-semibold text-dark truncate">
                          {meal.foods.join(", ")}
                        </h3>
                        <p className="font-body text-xs text-dark/50 mt-1">
                          {new Date(meal.created_at).toLocaleDateString("en-IN", {
                            day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
                          })}
                        </p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="font-body text-sm font-semibold text-primary">
                            {Math.round(meal.total_calories)} kcal
                          </span>
                          <span className="font-body text-xs text-dark/50">
                            Protein: {meal.protein_g.toFixed(1)}g
                          </span>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-dark/30 flex-shrink-0" />
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}

            {history.total > 10 && (
              <div className="flex justify-center gap-3 pt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="font-body text-sm text-dark/60 self-center">
                  Page {page}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * 10 >= history.total}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
