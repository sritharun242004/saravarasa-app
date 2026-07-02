"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/lib/use-toast";
import { submitLifestyleAudit, getAuditResult, getMe, type AuditSubmitResult } from "@/lib/api";
import { ArrowRight, ArrowLeft, CheckCircle2, Loader2, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Question model ────────────────────────────────────────────────────────────

type QType = "radio" | "scale" | "number" | "text";

interface Question {
  id: string;            // q7..q35, or profile field name for Section A
  label: string;
  type: QType;
  options?: { value: string; label: string }[];
  optional?: boolean;
  profile?: boolean;     // belongs to Section A (stored in section_a, not scored)
  placeholder?: string;
}

interface Section {
  id: string;
  title: string;
  emoji: string;
  description: string;
  questions: Question[];
}

const opt = (...labels: string[]) =>
  labels.map((label, i) => ({ value: String.fromCharCode(65 + i), label }));

// ─── The 35-question Lifestyle Audit (Phase 2 spec) ─────────────────────────────

const SECTIONS: Section[] = [
  {
    id: "profile",
    title: "Basic Profile",
    emoji: "👤",
    description: "A little context about your daily life. This part is not scored.",
    questions: [
      { id: "name", label: "What is your full name?", type: "text", profile: true, placeholder: "Your full name" },
      { id: "age", label: "How old are you?", type: "number", profile: true, placeholder: "18 – 70" },
      { id: "occupation", label: "What is your occupation?", type: "text", profile: true, placeholder: "e.g. Software Engineer, Teacher" },
      {
        id: "work_type", label: "What best describes your work type?", type: "radio", profile: true,
        options: opt(
          "Desk-based — I sit at a computer most of the day",
          "Mix — some desk work, some movement",
          "Active — on my feet or moving most of the day",
          "Shift work — my schedule changes regularly",
        ),
      },
      {
        id: "sitting_hours", label: "On a typical workday, how many hours do you spend sitting?", type: "radio", profile: true,
        options: opt("Less than 4 hours", "4 to 6 hours", "6 to 8 hours", "More than 8 hours"),
      },
      {
        id: "marital_status", label: "What is your marital status? (Optional)", type: "radio", profile: true, optional: true,
        options: opt("Single", "Married", "Other / prefer not to say"),
      },
    ],
  },
  {
    id: "sleep",
    title: "Sleep Audit",
    emoji: "🌙",
    description: "Sleep shapes hunger, energy and recovery.",
    questions: [
      { id: "q7", label: "What time do you usually go to sleep on weeknights?", type: "radio",
        options: opt("Before 10 PM", "10 PM to 11 PM", "11 PM to midnight", "Midnight to 1 AM", "After 1 AM") },
      { id: "q8", label: "What time do you usually wake up?", type: "radio",
        options: opt("Before 6 AM", "6 AM to 7 AM", "7 AM to 8 AM", "After 8 AM", "No fixed wake time — it depends") },
      { id: "q9", label: "On most nights, how many hours of actual sleep do you get?", type: "radio",
        options: opt("7 to 9 hours", "6 to 7 hours", "5 to 6 hours", "Less than 5 hours", "It varies a lot") },
      { id: "q10", label: "When you wake up, how do you feel?", type: "radio",
        options: opt("Rested and ready", "Groggy 10–15 min but okay after", "Tired — I want to sleep more", "Heavy and exhausted", "I never feel rested") },
      { id: "q11", label: "What do you usually do in the last 30 minutes before sleeping?", type: "radio",
        options: opt("Avoid screens — read, meditate, wind down", "Use phone occasionally but stop before sleep", "Scroll / watch until I feel sleepy", "On a screen right until I fall asleep", "I often fall asleep watching something") },
      { id: "q12", label: "How often do you have difficulty falling asleep?", type: "radio",
        options: opt("Never — I fall asleep easily", "Rarely — only occasionally", "Sometimes — a few nights a week", "Often — most nights", "Almost every night") },
    ],
  },
  {
    id: "food",
    title: "Food & Eating Habits",
    emoji: "🍱",
    description: "Your eating patterns and timing.",
    questions: [
      { id: "q13", label: "How many proper meals do you eat on a typical weekday? (Not counting tea, coffee or small snacks)", type: "radio",
        options: opt("3+ meals at roughly consistent times", "2 proper meals, fairly consistent", "2 proper meals but timing varies a lot", "1 proper meal most days", "I eat whenever I get time — no real pattern") },
      { id: "q14", label: "Are your meal timings regular or irregular?", type: "radio",
        options: opt("Very regular — same time every day", "Usually regular with occasional variation", "Irregular — shifts by hours depending on work", "Very irregular — no consistent timing at all") },
      { id: "q15", label: "What time do you usually finish dinner?", type: "radio",
        options: opt("Before 7:30 PM most days", "7:30 PM to 8:30 PM most days", "8:30 PM to 9:30 PM most days", "After 9:30 PM most days", "After 10:30 PM most days") },
      { id: "q16", label: "How often do you eat junk or processed food in a typical week?", type: "radio",
        options: opt("Rarely — once a month or less", "Occasionally — once or twice a week", "Often — 3 to 4 times a week", "Most days", "Almost every meal includes processed / outside food") },
      { id: "q17", label: "How often do you eat after 9 PM or late at night?", type: "radio",
        options: opt("Rarely — almost never", "Once or twice a week", "3 to 4 nights a week", "Most nights", "Every night") },
      { id: "q18", label: "How would you describe your sugar cravings?", type: "radio",
        options: opt("Low — I rarely crave sweets", "Moderate — I crave occasionally and can manage it", "High — I frequently crave and usually give in", "Very high — I need something sweet most days") },
      { id: "q19", label: "Do you eat differently when you are stressed, bored or upset?", type: "radio",
        options: opt("No — not strongly linked to my mood", "Sometimes — minor changes when stressed", "Often — I eat more or reach for specific foods", "Yes — food is my primary way of managing emotions") },
      { id: "q20", label: "How much water do you drink in a typical day?", type: "radio",
        options: opt("2 litres or more", "1 to 2 litres", "Less than 1 litre", "I am not sure — I do not track it") },
    ],
  },
  {
    id: "movement",
    title: "Movement & Activity",
    emoji: "🏃",
    description: "How much you move through the day.",
    questions: [
      { id: "q21", label: "How many days per week do you do any intentional physical activity? (Walking, exercise, yoga, sports)", type: "radio",
        options: opt("5 or more days", "3 to 4 days", "1 to 2 days", "Less than once a week", "I do not do any intentional physical activity") },
      { id: "q22", label: "On a typical day, how much do you walk in total?", type: "radio",
        options: opt("More than 30 minutes of walking", "15 to 30 minutes", "Less than 15 minutes", "Minimal — vehicles or lifts for almost everything") },
      { id: "q23", label: "How long do you sit continuously without getting up on a typical workday?", type: "radio",
        options: opt("Rarely more than 1 hour without moving", "1 to 2 hours at a stretch sometimes", "2 to 3 hours regularly without a break", "3 to 4 hours without getting up", "4 or more hours without getting up") },
      { id: "q24", label: "Do you experience any regular body pain or stiffness?", type: "radio",
        options: opt("No — my body feels fine generally", "Occasional minor stiffness — usually mornings", "Regular lower back or neck pain from sitting", "Daily pain or stiffness that affects how I move") },
      { id: "q25", label: "How would you describe your energy levels during the day?", type: "radio",
        options: opt("Consistently good — no significant dips", "Good in morning, slight afternoon dip", "Noticeable afternoon crash — need tea/coffee", "Low energy most of the day", "Exhausted most of the day regardless of sleep") },
    ],
  },
  {
    id: "stress",
    title: "Stress & Emotional Health",
    emoji: "🧘",
    description: "Stress is closely tied to eating and recovery.",
    questions: [
      { id: "q26", label: "On a scale of 1 to 10, how would you rate your current stress level? (1 = very low, 10 = overwhelming)", type: "scale" },
      { id: "q27", label: "What is your biggest source of stress right now?", type: "radio",
        options: opt("Work pressure — deadlines, performance, relationships at work", "Family or relationship situations", "Financial concerns", "Health concerns — my own or someone close", "Multiple areas simultaneously", "I am not under significant stress right now") },
      { id: "q28", label: "How often does your mood or emotional state fluctuate significantly during the day?", type: "radio",
        options: opt("Rarely — I am generally emotionally steady", "Occasionally — minor fluctuations", "Often — significant shifts most days", "Very often — unpredictable and hard to manage") },
      { id: "q29", label: "What is your primary motivation for joining this program?", type: "radio",
        options: opt("A specific health concern or doctor's advice", "I want to lose weight and feel better in my body", "I want more energy and better daily function", "I want to build sustainable habits before problems start", "Someone I know recommended it") },
      { id: "q30", label: "What has been your biggest challenge in maintaining healthy habits in the past?", type: "radio",
        options: opt("I do not have enough time", "I start but cannot stay consistent", "I lack support or accountability", "I find healthy food difficult to access or prepare", "Stress and emotional state derail me", "I have not seriously tried before") },
    ],
  },
  {
    id: "digestion",
    title: "Digestive & Functional Health",
    emoji: "🫁",
    description: "Digestion is a direct signal of metabolic function.",
    questions: [
      { id: "q31", label: "How often do you experience bloating or fullness and discomfort after meals?", type: "radio",
        options: opt("Rarely — only when I eat something unusual", "Occasionally — once or twice a week", "Often — several times a week", "Most days", "Almost every meal") },
      { id: "q32", label: "How would you describe your bowel movement pattern?", type: "radio",
        options: opt("Regular — once a day at roughly the same time", "Mostly regular — once a day but timing varies", "Once every 2 days or less frequently", "Irregular — I cannot predict when", "Constipation is a persistent concern for me") },
      { id: "q33", label: "How often do you experience acidity, heartburn or a burning sensation in your chest or stomach?", type: "radio",
        options: opt("Never or very rarely", "Once or twice a month", "Once or twice a week", "Most days", "Multiple times per day") },
      { id: "q34", label: "How would you describe your appetite?", type: "radio",
        options: opt("Consistent — hungry at regular times, stop when full", "Slightly variable — some days hungrier than others", "Unpredictable — my hunger fluctuates significantly", "I rarely feel genuinely hungry — I eat by habit", "I frequently overeat past the point of fullness") },
      { id: "q35", label: "How do you feel in the 30 to 60 minutes after a typical meal?", type: "radio",
        options: opt("Light and energised", "Neutral — neither energised nor heavy", "A little heavy or sluggish but it passes", "Heavy and tired — I often want to rest", "Very heavy and uncomfortable — almost every meal") },
    ],
  },
];

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";

type AnswerMap = Record<string, string>;

const ZONE_STYLES: Record<string, { ring: string; text: string; bg: string; emoji: string }> = {
  Green:  { ring: "border-accent/40",       text: "text-accent",      bg: "bg-accent/5",      emoji: "🟢" },
  Yellow: { ring: "border-yellow-400/50",   text: "text-yellow-600",  bg: "bg-yellow-50",     emoji: "🟡" },
  Orange: { ring: "border-orange-400/50",   text: "text-orange-600",  bg: "bg-orange-50",     emoji: "🟠" },
  Red:    { ring: "border-destructive/40",  text: "text-destructive", bg: "bg-destructive/5", emoji: "🔴" },
};

const ZONE_MESSAGES: Record<string, string> = {
  Green: "Your lifestyle is working for you in most areas. The program will sharpen what is already good and build on a strong foundation.",
  Yellow: "Your lifestyle has been drifting — not dramatically, but consistently. The good news is that drifting is reversible faster than it accumulated.",
  Orange: "Several areas of your lifestyle are working against your health at the same time. This is the most common pattern we see, and the one that responds most to structured intervention.",
  Red: "Your results show your body has been under sustained pressure for some time. We are glad you are here — one of our clinical team will reach out to understand your situation personally.",
};

export default function AuditPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [sectionIdx, setSectionIdx] = useState(0);
  const [answers, setAnswers] = useState<AnswerMap>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<AuditSubmitResult | null>(null);
  const [checking, setChecking] = useState(true);
  const [alreadyDone, setAlreadyDone] = useState(false);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  // Prefill name from the signed-in account.
  useEffect(() => {
    const name = typeof window !== "undefined" ? localStorage.getItem(CLIENT_NAME_KEY) : "";
    if (name) setAnswers((a) => ({ ...a, name: a.name || name }));
  }, []);

  // If the audit is already completed, show the saved result (read-only) — no retake.
  // Checks client.audit_completed first so we only ever call getAuditResult for
  // clients who actually have one — otherwise every first-time visitor would
  // trigger an expected-but-noisy 404 in the browser console.
  useEffect(() => {
    if (!clientId) {
      router.push("/login");
      return;
    }
    getMe()
      .then((me) => (me.audit_completed ? getAuditResult(clientId) : null))
      .then((r) => {
        if (!r) return;
        setResult({
          success: true,
          score: r.total_score,
          max_score: r.max_score,
          zone: r.zone,
          message: ZONE_MESSAGES[r.zone] || "",
          lowest_domain: r.lowest_domain,
          highest_domain: r.highest_domain,
          priority_intervention: r.priority_intervention,
          critical_flags: [],
          bnys_review_required: r.bnys_review_required,
        });
        setAlreadyDone(true);
      })
      .catch(() => {
        /* no prior result — show the questionnaire */
      })
      .finally(() => setChecking(false));
  }, [clientId, router]);

  const totalSections = SECTIONS.length;
  const section = SECTIONS[sectionIdx];
  const progress = Math.round(((sectionIdx + 1) / totalSections) * 100);

  const setValue = (id: string, value: string) => setAnswers((p) => ({ ...p, [id]: value }));

  const sectionComplete = section.questions.every(
    (q) => q.optional || (answers[q.id] !== undefined && answers[q.id] !== ""),
  );

  const buildResponses = (): Record<string, unknown> => {
    const section_a: Record<string, unknown> = {};
    const out: Record<string, unknown> = {};
    for (const s of SECTIONS) {
      for (const q of s.questions) {
        const val = answers[q.id];
        if (val === undefined || val === "") continue;
        if (q.profile) {
          section_a[q.id] = q.id === "age" ? Number(val) : val;
        } else {
          out[q.id] = val;
        }
      }
    }
    out.section_a = section_a;
    // Context aliases the evaluation engine expects.
    out.q27_text = answers.q27 || "";
    out.q29_text = answers.q29 || "";
    out.q30_selection = answers.q30 || "";
    return out;
  };

  const goNext = async () => {
    if (!sectionComplete) {
      toast({ title: "Please answer all questions on this screen", variant: "destructive" });
      return;
    }
    if (sectionIdx < totalSections - 1) {
      setSectionIdx((i) => i + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    // Final submit
    if (!clientId) {
      router.push("/login");
      return;
    }
    setSubmitting(true);
    try {
      const res = await submitLifestyleAudit(clientId, buildResponses());
      setResult(res);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Could not submit your audit. Please try again.";
      toast({ title: "Error", description: msg, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const goBack = () => {
    if (sectionIdx > 0) {
      setSectionIdx((i) => i - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const isLastSection = sectionIdx === totalSections - 1;

  // ─── Checking for an existing result ────────────────────────────────────────
  if (checking) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  // ─── Results screen ──────────────────────────────────────────────────────────
  if (result) {
    const z = ZONE_STYLES[result.zone] || ZONE_STYLES.Yellow;
    const pct = Math.round((result.score / result.max_score) * 100);
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Trophy className="w-8 h-8 text-primary" />
            </div>
            <h1 className="font-heading text-3xl font-bold text-dark">Your Lifestyle Audit Result</h1>
            <p className="font-body text-dark/60 mt-1">
              {alreadyDone
                ? "You've already completed this assessment — here's your result."
                : "Based on your 35 answers across 5 health domains."}
            </p>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.05 }}>
            <Card className={cn("border-2", z.ring, z.bg)}>
              <CardContent className="p-8 text-center">
                <div className="text-5xl mb-3">{z.emoji}</div>
                <p className={cn("font-heading text-2xl font-bold mb-1", z.text)}>{result.zone} Zone</p>
                <p className="font-heading text-5xl font-bold text-dark mt-4">
                  {result.score}
                  <span className="text-2xl text-dark/40 font-body"> / {result.max_score}</span>
                </p>
                <div className="mt-4">
                  <Progress value={pct} className="h-3" />
                  <p className="font-body text-xs text-dark/50 mt-2">{pct}% lifestyle score</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card>
              <CardContent className="p-6">
                <p className="font-body text-dark/80 leading-relaxed">{result.message}</p>
                <div className="grid grid-cols-2 gap-3 mt-5">
                  <div className="rounded-xl bg-muted/50 p-3">
                    <p className="font-body text-xs text-dark/40">Strongest area</p>
                    <p className="font-body text-sm font-semibold text-dark">{result.highest_domain}</p>
                  </div>
                  <div className="rounded-xl bg-muted/50 p-3">
                    <p className="font-body text-xs text-dark/40">Focus area</p>
                    <p className="font-body text-sm font-semibold text-dark">{result.lowest_domain}</p>
                  </div>
                </div>
                {result.bnys_review_required && (
                  <div className="mt-4 p-3 rounded-xl bg-primary/5 border border-primary/20">
                    <p className="font-body text-sm text-dark/70">
                      One of our clinical team members will reach out to understand your situation personally before
                      designing your program.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={() => router.push("/profile")}>
              View Profile
            </Button>
            <Button className="flex-1" onClick={() => router.push("/descriptive-test")}>
              Next Assessment <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </AppShell>
    );
  }

  // ─── Question wizard ─────────────────────────────────────────────────────────
  return (
    <AppShell>
      <div className="min-h-screen px-4 py-8 max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <h1 className="font-heading text-3xl font-bold text-dark">Lifestyle Audit</h1>
          <p className="font-body text-dark/60 mt-1">
            A picture of your life right now. Answer based on what actually happens — there are no wrong answers.
          </p>
        </motion.div>

        <div className="mb-8">
          <div className="flex justify-between text-xs font-body text-dark/50 mb-2">
            <span>Section {sectionIdx + 1} of {totalSections}</span>
            <span>{progress}% complete</span>
          </div>
          <Progress value={progress} className="h-2" />
          <div className="flex gap-1 mt-3">
            {SECTIONS.map((s, i) => (
              <div key={s.id} className={cn(
                "flex-1 h-1 rounded-full transition-colors duration-300",
                i < sectionIdx ? "bg-primary" : i === sectionIdx ? "bg-primary/50" : "bg-muted",
              )} />
            ))}
          </div>
        </div>

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

                <div className="space-y-7">
                  {section.questions.map((q) => (
                    <div key={q.id}>
                      <label className="block font-body text-sm font-medium text-dark mb-3">{q.label}</label>

                      {q.type === "radio" && q.options && (
                        <div className="grid grid-cols-1 gap-2">
                          {q.options.map((o) => (
                            <button
                              key={o.value}
                              type="button"
                              onClick={() => setValue(q.id, o.value)}
                              className={cn(
                                "w-full text-left px-4 py-3 rounded-xl border font-body text-sm transition-all duration-200",
                                answers[q.id] === o.value
                                  ? "border-primary bg-primary/5 text-dark font-medium"
                                  : "border-border bg-card text-dark/70 hover:border-primary/40",
                              )}
                            >
                              <div className="flex items-center gap-2.5">
                                <div className={cn(
                                  "w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0",
                                  answers[q.id] === o.value ? "border-primary" : "border-dark/20",
                                )}>
                                  {answers[q.id] === o.value && <div className="w-2 h-2 rounded-full bg-primary" />}
                                </div>
                                {o.label}
                              </div>
                            </button>
                          ))}
                        </div>
                      )}

                      {q.type === "scale" && (
                        <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
                          {Array.from({ length: 10 }, (_, i) => String(i + 1)).map((n) => (
                            <button
                              key={n}
                              type="button"
                              onClick={() => setValue(q.id, n)}
                              className={cn(
                                "py-3 rounded-xl border font-body text-sm font-semibold transition-all duration-200",
                                answers[q.id] === n
                                  ? "border-primary bg-primary text-white"
                                  : "border-border bg-card text-dark/70 hover:border-primary/40",
                              )}
                            >
                              {n}
                            </button>
                          ))}
                        </div>
                      )}

                      {q.type === "number" && (
                        <input
                          type="number"
                          inputMode="numeric"
                          min={18}
                          max={70}
                          placeholder={q.placeholder}
                          value={answers[q.id] || ""}
                          onChange={(e) => setValue(q.id, e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                      )}

                      {q.type === "text" && (
                        <input
                          type="text"
                          placeholder={q.placeholder}
                          value={answers[q.id] || ""}
                          onChange={(e) => setValue(q.id, e.target.value)}
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

        <div className="flex gap-3">
          {sectionIdx > 0 && (
            <Button variant="outline" onClick={goBack} className="flex-1" disabled={submitting}>
              <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>
          )}
          <Button onClick={goNext} disabled={submitting} className="flex-1">
            {submitting ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Scoring…</>
            ) : isLastSection ? (
              <><CheckCircle2 className="w-4 h-4 mr-2" />Submit & See My Result</>
            ) : (
              <>Next <ArrowRight className="w-4 h-4 ml-2" /></>
            )}
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
