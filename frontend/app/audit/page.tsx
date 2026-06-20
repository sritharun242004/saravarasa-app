"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/lib/use-toast";
import { saveAudit } from "@/lib/api";
import { ArrowRight, ArrowLeft, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Types ───────────────────────────────────────────────────────────────────

type AuditData = Record<string, string | boolean | undefined>;

interface OptionGroup {
  label: string;
  value: string;
}

interface Question {
  key: string;
  label: string;
  type: "radio" | "boolean" | "text";
  options?: OptionGroup[];
  placeholder?: string;
}

interface Section {
  id: string;
  title: string;
  emoji: string;
  description: string;
  questions: Question[];
}

// ─── Sections ────────────────────────────────────────────────────────────────

const SECTIONS: Section[] = [
  {
    id: "profile",
    title: "Basic Profile",
    emoji: "👤",
    description: "Tell us a little about your daily life.",
    questions: [
      { key: "city", label: "Which city do you live in?", type: "text", placeholder: "e.g. Chennai, Bangalore..." },
      { key: "occupation", label: "What is your occupation?", type: "text", placeholder: "e.g. IT professional, homemaker..." },
      {
        key: "cooking_at_home", label: "Do you usually cook at home?", type: "boolean",
      },
    ],
  },
  {
    id: "sleep",
    title: "Sleep Audit",
    emoji: "🌙",
    description: "Sleep affects your food choices and hunger patterns.",
    questions: [
      {
        key: "sleep_hours", label: "How many hours do you sleep per night?", type: "radio",
        options: [
          { label: "Less than 6 hours", value: "less_than_6" },
          { label: "6–7 hours", value: "6_to_7" },
          { label: "7–8 hours", value: "7_to_8" },
          { label: "More than 8 hours", value: "more_than_8" },
        ],
      },
      {
        key: "sleep_quality", label: "How would you rate your sleep quality?", type: "radio",
        options: [
          { label: "Poor — I wake up tired", value: "poor" },
          { label: "Average — okay most days", value: "average" },
          { label: "Good — I feel rested", value: "good" },
        ],
      },
      { key: "wake_time", label: "What time do you usually wake up?", type: "text", placeholder: "e.g. 6:30 AM" },
    ],
  },
  {
    id: "food_habits",
    title: "Food Habits",
    emoji: "🍱",
    description: "Help us understand your current eating patterns.",
    questions: [
      {
        key: "meals_per_day", label: "How many meals do you eat per day?", type: "radio",
        options: [
          { label: "1–2 meals", value: "1_to_2" },
          { label: "3 meals", value: "3" },
          { label: "4 or more meals", value: "4_or_more" },
        ],
      },
      {
        key: "breakfast_habit", label: "How often do you eat breakfast?", type: "radio",
        options: [
          { label: "Always", value: "always" },
          { label: "Sometimes", value: "sometimes" },
          { label: "Rarely", value: "rarely" },
          { label: "Never — I skip it", value: "never" },
        ],
      },
      {
        key: "water_intake", label: "How much water do you drink daily?", type: "radio",
        options: [
          { label: "Less than 1 litre", value: "less_than_1L" },
          { label: "1–2 litres", value: "1_to_2L" },
          { label: "More than 2 litres", value: "more_than_2L" },
        ],
      },
      {
        key: "outside_food_frequency", label: "How often do you eat outside / order food?", type: "radio",
        options: [
          { label: "Daily", value: "daily" },
          { label: "A few times a week", value: "few_times_week" },
          { label: "Rarely", value: "rarely" },
        ],
      },
      {
        key: "sugary_beverage_frequency", label: "How often do you have sugary drinks (tea with sugar, cold drinks, juices)?", type: "radio",
        options: [
          { label: "Multiple times daily", value: "multiple_daily" },
          { label: "Once a day", value: "once_daily" },
          { label: "A few times a week", value: "few_times_week" },
          { label: "Rarely", value: "rarely" },
        ],
      },
      {
        key: "processed_food_frequency", label: "How often do you eat packaged/processed snacks?", type: "radio",
        options: [
          { label: "Daily", value: "daily" },
          { label: "A few times a week", value: "few_times_week" },
          { label: "Rarely", value: "rarely" },
        ],
      },
    ],
  },
  {
    id: "movement",
    title: "Movement",
    emoji: "🏃",
    description: "Physical activity and movement patterns.",
    questions: [
      {
        key: "activity_level", label: "How would you describe your general activity level?", type: "radio",
        options: [
          { label: "Sedentary — mostly sitting all day", value: "sedentary" },
          { label: "Lightly active — some walking", value: "lightly_active" },
          { label: "Moderately active — regular movement", value: "moderately_active" },
          { label: "Very active — physical work or daily exercise", value: "very_active" },
        ],
      },
      {
        key: "exercise_frequency", label: "How often do you exercise or work out?", type: "radio",
        options: [
          { label: "Never", value: "never" },
          { label: "1–2 times a week", value: "1_to_2_week" },
          { label: "3–5 times a week", value: "3_to_5_week" },
          { label: "Daily", value: "daily" },
        ],
      },
    ],
  },
  {
    id: "stress",
    title: "Stress",
    emoji: "🧘",
    description: "Stress has a strong connection with eating patterns.",
    questions: [
      {
        key: "stress_level", label: "How would you rate your average stress level?", type: "radio",
        options: [
          { label: "Low — generally calm", value: "low" },
          { label: "Moderate — some daily stress", value: "moderate" },
          { label: "High — frequently stressed", value: "high" },
        ],
      },
      {
        key: "stress_eating", label: "Do you tend to eat more when stressed?", type: "radio",
        options: [
          { label: "Yes, definitely", value: "yes" },
          { label: "Sometimes", value: "sometimes" },
          { label: "No, stress reduces my appetite", value: "no" },
        ],
      },
    ],
  },
  {
    id: "digestion",
    title: "Digestive Health",
    emoji: "🫁",
    description: "Digestive health reflects your overall food relationship.",
    questions: [
      {
        key: "bowel_regularity", label: "How regular are your bowel movements?", type: "radio",
        options: [
          { label: "Regular — once or twice daily", value: "regular" },
          { label: "Irregular — varies a lot", value: "irregular" },
        ],
      },
      {
        key: "digestion_issues", label: "Do you experience digestive discomfort (bloating, acidity, constipation)?", type: "boolean",
      },
      { key: "digestion_notes", label: "Any specific digestive concerns? (optional)", type: "text", placeholder: "Describe if any..." },
      { key: "health_goals", label: "What health goal matters most to you right now?", type: "text", placeholder: "e.g. More energy, better sleep, reduce bloating..." },
      { key: "dietary_restrictions", label: "Any dietary restrictions or food allergies? (optional)", type: "text", placeholder: "e.g. Vegetarian, lactose intolerant..." },
    ],
  },
];

// ─── Component ───────────────────────────────────────────────────────────────

const CLIENT_ID_KEY = "sarvarasa_client_id";

function getClientId(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(CLIENT_ID_KEY) || "";
}

export default function AuditPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [sectionIdx, setSectionIdx] = useState(0);
  const [data, setData] = useState<AuditData>({});
  const [saving, setSaving] = useState(false);

  const totalSections = SECTIONS.length;
  const section = SECTIONS[sectionIdx];
  const progress = Math.round(((sectionIdx) / totalSections) * 100);

  const setValue = (key: string, value: string | boolean) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const autoSave = useCallback(async (payload: AuditData) => {
    const clientId = getClientId();
    if (!clientId) return;
    setSaving(true);
    try {
      await saveAudit({ client_id: clientId, ...payload, completed: false });
    } catch {
      // silent auto-save
    } finally {
      setSaving(false);
    }
  }, []);

  const goNext = async () => {
    await autoSave(data);
    if (sectionIdx < totalSections - 1) {
      setSectionIdx((i) => i + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      // Final submit
      const clientId = getClientId();
      if (!clientId) {
        toast({ title: "Not registered", description: "Please register before completing the audit.", variant: "destructive" });
        router.push("/onboarding");
        return;
      }
      setSaving(true);
      try {
        await saveAudit({ client_id: clientId, ...data, completed: true });
        toast({ title: "Audit complete!", description: "Your 7-day challenge is now unlocked." });
        router.push("/challenge");
      } catch {
        toast({ title: "Error", description: "Could not save audit. Please try again.", variant: "destructive" });
      } finally {
        setSaving(false);
      }
    }
  };

  const goBack = () => {
    if (sectionIdx > 0) {
      setSectionIdx((i) => i - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const isLastSection = sectionIdx === totalSections - 1;

  return (
    <AppShell>
      <div className="min-h-screen px-4 py-8 max-w-2xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <h1 className="font-heading text-3xl font-bold text-dark">Lifestyle Audit</h1>
          <p className="font-body text-dark/60 mt-1">Help us understand your current lifestyle before the challenge.</p>
        </motion.div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between text-xs font-body text-dark/50 mb-2">
            <span>Section {sectionIdx + 1} of {totalSections}</span>
            <span>{saving ? "Saving…" : `${progress}% complete`}</span>
          </div>
          <Progress value={progress + (100 / totalSections)} className="h-2" />
          <div className="flex gap-1 mt-3">
            {SECTIONS.map((s, i) => (
              <div
                key={s.id}
                className={cn(
                  "flex-1 h-1 rounded-full transition-colors duration-300",
                  i < sectionIdx ? "bg-primary" : i === sectionIdx ? "bg-primary/50" : "bg-muted"
                )}
              />
            ))}
          </div>
        </div>

        {/* Section Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={section.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="mb-6">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-2xl">
                    {section.emoji}
                  </div>
                  <div>
                    <h2 className="font-heading text-xl font-semibold text-dark">{section.title}</h2>
                    <p className="font-body text-sm text-dark/60">{section.description}</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {section.questions.map((q) => (
                    <div key={q.key}>
                      <label className="block font-body text-sm font-medium text-dark mb-3">{q.label}</label>

                      {q.type === "radio" && q.options && (
                        <div className="grid grid-cols-1 gap-2">
                          {q.options.map((opt) => (
                            <button
                              key={opt.value}
                              type="button"
                              onClick={() => setValue(q.key, opt.value)}
                              className={cn(
                                "w-full text-left px-4 py-3 rounded-xl border font-body text-sm transition-all duration-200",
                                data[q.key] === opt.value
                                  ? "border-primary bg-primary/5 text-dark font-medium"
                                  : "border-border bg-card text-dark/70 hover:border-primary/40"
                              )}
                            >
                              <div className="flex items-center gap-2">
                                <div className={cn(
                                  "w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0",
                                  data[q.key] === opt.value ? "border-primary" : "border-dark/20"
                                )}>
                                  {data[q.key] === opt.value && (
                                    <div className="w-2 h-2 rounded-full bg-primary" />
                                  )}
                                </div>
                                {opt.label}
                              </div>
                            </button>
                          ))}
                        </div>
                      )}

                      {q.type === "boolean" && (
                        <div className="flex gap-3">
                          {[{ label: "Yes", value: true }, { label: "No", value: false }].map((opt) => (
                            <button
                              key={String(opt.value)}
                              type="button"
                              onClick={() => setValue(q.key, opt.value)}
                              className={cn(
                                "flex-1 py-3 rounded-xl border font-body text-sm font-medium transition-all duration-200",
                                data[q.key] === opt.value
                                  ? "border-primary bg-primary/5 text-primary"
                                  : "border-border bg-card text-dark/70 hover:border-primary/40"
                              )}
                            >
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      )}

                      {q.type === "text" && (
                        <input
                          type="text"
                          placeholder={q.placeholder}
                          value={(data[q.key] as string) || ""}
                          onChange={(e) => setValue(q.key, e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex gap-3">
          {sectionIdx > 0 && (
            <Button variant="outline" onClick={goBack} className="flex-1">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          )}
          <Button onClick={goNext} disabled={saving} className="flex-1">
            {isLastSection ? (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Complete Audit & Start Challenge
              </>
            ) : (
              <>
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </div>

        <p className="font-body text-xs text-dark/40 text-center mt-4">
          Progress is auto-saved. You can return and continue anytime.
        </p>
      </div>
    </AppShell>
  );
}
