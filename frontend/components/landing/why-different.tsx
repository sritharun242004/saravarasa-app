"use client";

import { motion } from "framer-motion";
import { X, Check } from "lucide-react";

const oldApproach = [
  "Calorie counting every gram",
  "Meal replacement shakes",
  "Generic \"Indian food\" categories",
  "Weight-loss score cards",
  "Restrictive diet plans",
];

const sarvarasaApproach = [
  "No calorie counting — just awareness",
  "Your everyday meals, tracked simply",
  "Photo + description is all you need",
  "Food pattern insights, not scores",
  "Education, not restriction",
  "Traditional Indian food celebrated",
];

export function WhyDifferent() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold font-body text-sm uppercase tracking-widest">A Different Philosophy</span>
          <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mt-3 mb-4">
            Awareness, Not Restriction
          </h2>
          <p className="text-dark/60 font-body text-lg max-w-xl mx-auto">
            Most food apps make you count, measure, and restrict. Sarvarasa helps you observe, understand, and improve.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="bg-card rounded-3xl p-8 border border-border/50 shadow-card"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-destructive/10 flex items-center justify-center">
                <X className="w-5 h-5 text-destructive" />
              </div>
              <h3 className="font-heading text-xl font-semibold text-dark">Old Approach</h3>
            </div>
            <div className="space-y-3">
              {oldApproach.map((item) => (
                <div key={item} className="flex items-center gap-3 py-2.5 px-4 bg-muted rounded-xl">
                  <X className="w-4 h-4 text-destructive flex-shrink-0" />
                  <span className="font-body text-dark/70">{item}</span>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-card rounded-3xl p-8 border border-primary/20 shadow-card relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -translate-y-16 translate-x-16" />
            <div className="flex items-center gap-3 mb-6 relative">
              <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center">
                <Check className="w-5 h-5 text-accent" />
              </div>
              <h3 className="font-heading text-xl font-semibold text-dark">Sarvarasa Way</h3>
            </div>
            <div className="space-y-3 relative">
              {sarvarasaApproach.map((item) => (
                <div key={item} className="flex items-center gap-3 py-2.5 px-4 bg-accent/5 rounded-xl border border-accent/10">
                  <Check className="w-4 h-4 text-accent flex-shrink-0" />
                  <span className="font-body text-dark font-medium">{item}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
