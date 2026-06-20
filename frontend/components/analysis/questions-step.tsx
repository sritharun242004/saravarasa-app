"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { generateQuestions, calculateNutrition, type AnalyzeImageResponse, type QuestionsResponse } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "@/lib/use-toast";
import { ChevronRight, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  analysisResult: AnalyzeImageResponse;
  onComplete: (result: QuestionsResponse) => void;
}

export function QuestionsStep({ analysisResult, onComplete }: Props) {
  const router = useRouter();
  const [questions, setQuestions] = useState<QuestionsResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentQ, setCurrentQ] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const result = await generateQuestions(
          analysisResult.session_id,
          analysisResult.foods.map((f) => f.name)
        );
        setQuestions(result);
      } catch {
        toast({ title: "Error loading questions", variant: "destructive" });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [analysisResult]);

  const handleAnswer = (qId: string, answer: string) => {
    const newAnswers = { ...answers, [qId]: answer };
    setAnswers(newAnswers);

    if (questions && currentQ < questions.questions.length - 1) {
      setTimeout(() => setCurrentQ((c) => c + 1), 300);
    }
  };

  const handleSubmit = async () => {
    if (!questions) return;
    setSubmitting(true);
    try {
      const result = await calculateNutrition(analysisResult.session_id, answers);
      router.push(`/results/${result.meal_id}`);
    } catch {
      toast({ title: "Calculation failed", description: "Please try again.", variant: "destructive" });
      setSubmitting(false);
    }
  };

  const allAnswered = questions
    ? questions.questions.every((q) => answers[q.id])
    : false;

  if (loading) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16">
        <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
        <p className="font-body text-dark/60">Generating smart questions...</p>
      </motion.div>
    );
  }

  if (!questions) return null;

  const q = questions.questions[currentQ];

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Badge variant="default">
            Detected: {analysisResult.foods[0]?.display_name || analysisResult.foods[0]?.name}
          </Badge>
          <Badge variant="muted">
            {Math.round(analysisResult.foods[0]?.confidence * 100)}% confident
          </Badge>
        </div>
        <div className="flex gap-1.5 mb-6">
          {questions.questions.map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-1 flex-1 rounded-full transition-all duration-300",
                i < currentQ ? "bg-primary" : i === currentQ ? "bg-primary/60" : "bg-muted"
              )}
            />
          ))}
        </div>
        <p className="font-body text-xs text-dark/50 mb-2">
          Question {currentQ + 1} of {questions.questions.length}
        </p>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={q.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.25 }}
        >
          <div className="bg-card rounded-2xl p-6 border border-border/50 shadow-soft mb-4">
            <h3 className="font-heading text-xl font-semibold text-dark mb-6">{q.question}</h3>
            <div className="grid grid-cols-2 gap-3">
              {q.options.map((option) => (
                <button
                  key={option}
                  onClick={() => handleAnswer(q.id, option)}
                  className={cn(
                    "py-4 px-4 rounded-xl border-2 font-body font-medium text-sm transition-all duration-200 cursor-pointer text-center",
                    answers[q.id] === option
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-muted/50 text-dark/70 hover:border-primary/40 hover:bg-primary/5"
                  )}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {currentQ < questions.questions.length - 1 && answers[q.id] && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Button
            variant="ghost"
            className="w-full"
            onClick={() => setCurrentQ((c) => c + 1)}
          >
            Next Question <ChevronRight className="w-4 h-4" />
          </Button>
        </motion.div>
      )}

      {allAnswered && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4"
        >
          <Button size="lg" className="w-full" onClick={handleSubmit} loading={submitting}>
            {submitting ? "Calculating..." : "Get My Nutrition Report"}
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
}
