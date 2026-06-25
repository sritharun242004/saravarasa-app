"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { getTestQuestions, submitDescriptive, type TestQuestion } from "@/lib/api";
import { Loader2, PenTool, CheckCircle2, ArrowRight } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";

// Fallback prompts shown when no descriptive questions are seeded in the backend.
const FALLBACK_QUESTIONS: TestQuestion[] = [
  { id: "fallback_1", test_type: "DESCRIPTIVE", question_text: "Describe your typical eating day from morning to night. What does a normal day on your plate look like?" },
  { id: "fallback_2", test_type: "DESCRIPTIVE", question_text: "What changes did you notice in your energy, digestion, or cravings during the 7-day challenge?" },
  { id: "fallback_3", test_type: "DESCRIPTIVE", question_text: "What is the biggest obstacle that stops you from eating the way you want to?" },
  { id: "fallback_4", test_type: "DESCRIPTIVE", question_text: "What is one realistic food habit you are willing to commit to for the next month?" },
];

export default function DescriptiveTestPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [questions, setQuestions] = useState<TestQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) {
      router.push("/login");
      return;
    }
    getTestQuestions(clientId, "DESCRIPTIVE")
      .then((qs) => setQuestions(qs.length > 0 ? qs : FALLBACK_QUESTIONS))
      .catch(() => setQuestions(FALLBACK_QUESTIONS))
      .finally(() => setLoading(false));
  }, [clientId, router]);

  const setAnswer = (id: string, val: string) => setAnswers((a) => ({ ...a, [id]: val }));

  const handleSubmit = async () => {
    const answered = questions.filter((q) => (answers[q.id] || "").trim().length > 0);
    if (answered.length === 0) {
      toast({ title: "Please answer at least one question", variant: "destructive" });
      return;
    }
    setSubmitting(true);
    try {
      await submitDescriptive(clientId, answers);
      setSubmitted(true);
      toast({ title: "Submitted!", description: "Your descriptive assessment has been saved." });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Could not submit. Please try again.";
      toast({ title: "Error", description: msg, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (submitted) {
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-5">
              <CheckCircle2 className="w-8 h-8 text-accent" />
            </div>
            <h1 className="font-heading text-2xl font-bold text-dark mb-2">Assessment Complete</h1>
            <p className="font-body text-dark/60 mb-8">
              Thanks for sharing. Your descriptive responses help us tailor your wellness recommendations.
            </p>
            <Button onClick={() => router.push("/profile")}>
              Go to Profile <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </motion.div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <PenTool className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="font-body text-[11px] font-semibold uppercase tracking-widest text-primary/70">Assessment 3</p>
              <h1 className="font-heading text-2xl font-bold text-dark">Descriptive Test</h1>
            </div>
          </div>
          <p className="font-body text-sm text-dark/60 mt-1">
            Tell us about your eating habits in your own words. There are no right or wrong answers.
          </p>
        </motion.div>

        {questions.map((q, idx) => (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * idx }}
          >
            <Card>
              <CardContent className="p-5">
                <label className="block font-body text-sm font-medium text-dark mb-3">
                  <span className="text-primary font-bold mr-1">{idx + 1}.</span> {q.question_text}
                </label>
                <textarea
                  value={answers[q.id] || ""}
                  onChange={(e) => setAnswer(q.id, e.target.value)}
                  rows={4}
                  placeholder="Type your answer here…"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-y"
                />
              </CardContent>
            </Card>
          </motion.div>
        ))}

        <Button onClick={handleSubmit} disabled={submitting} size="lg" className="w-full">
          {submitting ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Submitting…</>
          ) : (
            <>Submit Assessment <ArrowRight className="w-4 h-4 ml-2" /></>
          )}
        </Button>
      </div>
    </AppShell>
  );
}
