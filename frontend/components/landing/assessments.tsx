"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Camera, ClipboardList, PenTool, ArrowRight } from "lucide-react";

const assessments = [
  {
    number: 1,
    title: "7-Day Food Upload Challenge",
    tagline: "Track what you actually eat",
    description:
      "Upload your meals (breakfast, lunch and dinner) every day for 7 days. Real food, real photos, no measuring or calorie counting.",
    icon: Camera,
    href: "/challenge",
    cta: "Start Challenge",
    radius: "rounded-[2rem] rounded-tl-[4rem]",
    points: ["Daily meal uploads", "Build real food awareness", "85% consistency to qualify"],
  },
  {
    number: 2,
    title: "Lifestyle Audit",
    tagline: "Understand your habits",
    description:
      "A 35-question assessment across sleep, movement, stress, food and digestion that maps your current lifestyle into a health zone.",
    icon: ClipboardList,
    href: "/audit",
    cta: "Take the Audit",
    radius: "rounded-[2rem] rounded-br-[4rem]",
    points: ["Sleep, stress & digestion", "Scored health zone", "Personalised insights"],
  },
  {
    number: 3,
    title: "Descriptive Test",
    tagline: "Tell your story in your words",
    description:
      "Answer open-ended questions about your relationship with food. Your responses shape your personalised wellness recommendations.",
    icon: PenTool,
    href: "/descriptive-test",
    cta: "Begin Test",
    radius: "rounded-[2rem] rounded-tr-[4rem]",
    points: ["Open-ended reflection", "Deeper personalisation", "Long-term guidance"],
  },
];

export function Assessments() {
  return (
    <section id="assessments" className="relative py-28 px-4 sm:px-6 lg:px-8 bg-stone/40 overflow-hidden">
      <div className="absolute top-10 -left-20 w-80 h-80 bg-primary/10 blur-3xl blob-4 pointer-events-none" />
      <div className="absolute bottom-0 -right-16 w-72 h-72 bg-secondary/10 blur-3xl blob-1 pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16 max-w-3xl mx-auto"
        >
          <span className="inline-block bg-secondary/15 text-secondary rounded-full px-4 py-1.5 text-sm font-bold font-body mb-5">
            Three Assessments, One Journey
          </span>
          <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mb-4 text-balance">
            How Sarvarasa Works
          </h2>
          <p className="text-muted-foreground text-lg font-body text-balance">
            Complete three simple assessments inside the app to understand your eating patterns and unlock
            personalised wellness insights.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {assessments.map((a, idx) => {
            const Icon = a.icon;
            return (
              <motion.div
                key={a.number}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: idx * 0.12 }}
                viewport={{ once: true }}
              >
                <div
                  className={`group h-full bg-card border border-border/60 shadow-soft p-8 flex flex-col transition-all duration-300 hover:-translate-y-1 hover:shadow-float ${a.radius}`}
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center transition-colors duration-300 group-hover:bg-primary">
                      <Icon className="w-7 h-7 text-primary transition-colors duration-300 group-hover:text-primary-foreground" />
                    </div>
                    <span className="font-heading text-5xl font-bold text-muted/80 group-hover:text-secondary/30 transition-colors">
                      {a.number}
                    </span>
                  </div>

                  <p className="font-body text-xs font-bold uppercase tracking-widest text-secondary mb-1.5">
                    {a.tagline}
                  </p>
                  <h3 className="font-heading text-xl font-bold text-dark mb-3">{a.title}</h3>
                  <p className="font-body text-muted-foreground text-sm mb-6 leading-relaxed">{a.description}</p>

                  <ul className="space-y-2.5 mb-7">
                    {a.points.map((p) => (
                      <li key={p} className="flex items-start gap-2.5 text-sm font-body text-dark/70">
                        <span className="w-5 h-5 rounded-full bg-accent/15 flex items-center justify-center shrink-0 mt-0.5">
                          <span className="text-accent text-xs font-bold">✓</span>
                        </span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>

                  <Link href={a.href} className="mt-auto">
                    <span className="inline-flex items-center gap-2 font-body text-sm font-bold text-primary group-hover:gap-3 transition-all">
                      {a.cta} <ArrowRight className="w-4 h-4" />
                    </span>
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mt-14 font-body text-sm text-muted-foreground"
        >
          All three assessments are completed inside the app after you sign up.
        </motion.p>
      </div>
    </section>
  );
}
