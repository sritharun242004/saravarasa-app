"use client";

import { motion } from "framer-motion";
import { ClipboardList, Camera, BarChart2, Award } from "lucide-react";

const steps = [
  {
    icon: ClipboardList,
    step: "01",
    title: "Lifestyle Audit",
    description: "Complete a quick audit about your sleep, food habits, activity, and stress. Takes about 5 minutes.",
    color: "bg-primary/10 text-primary",
    border: "border-primary/20",
  },
  {
    icon: Camera,
    step: "02",
    title: "7-Day Meal Tracking",
    description: "Log your breakfast, lunch, and dinner every day with a photo and description. Use your everyday meals.",
    color: "bg-accent/10 text-accent",
    border: "border-accent/20",
  },
  {
    icon: BarChart2,
    step: "03",
    title: "Food Pattern Analysis",
    description: "We observe your food patterns — vegetable presence, protein sources, processed foods, meal consistency.",
    color: "bg-secondary/30 text-dark",
    border: "border-secondary/40",
  },
  {
    icon: Award,
    step: "04",
    title: "Personalized Report",
    description: "Receive food awareness insights, wholesome eating education, and your program qualification status.",
    color: "bg-primary/10 text-primary",
    border: "border-primary/20",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-4 bg-warm-gradient">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold font-body text-sm uppercase tracking-widest">The Journey</span>
          <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mt-3 mb-4">
            How It Works
          </h2>
          <p className="text-dark/60 font-body text-lg max-w-xl mx-auto">
            Four steps from lifestyle audit to a personalized food awareness report.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, i) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
            >
              <div className="bg-card rounded-3xl p-6 shadow-card border border-border/50 hover:shadow-elevated transition-shadow duration-300 h-full">
                <div className="flex items-start justify-between mb-5">
                  <div className={`w-12 h-12 rounded-2xl ${step.color} border ${step.border} flex items-center justify-center`}>
                    <step.icon className="w-5 h-5" />
                  </div>
                  <span className="font-heading text-5xl font-bold text-dark/5 leading-none">{step.step}</span>
                </div>
                <h3 className="font-heading text-lg font-semibold text-dark mb-2">{step.title}</h3>
                <p className="font-body text-dark/60 leading-relaxed text-sm">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
