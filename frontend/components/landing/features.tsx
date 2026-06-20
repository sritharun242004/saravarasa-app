"use client";

import { motion } from "framer-motion";
import { Camera, Leaf, BarChart2, FileText, Award, ShieldCheck } from "lucide-react";

const features = [
  {
    icon: Camera,
    title: "Photo + Description",
    description: "Upload a photo and describe your meal in your own words. No weighing, no measuring.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: Leaf,
    title: "Food Pattern Analysis",
    description: "We look for vegetables, proteins, fruits, traditional foods, and processed items — not calories.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: BarChart2,
    title: "Compliance Tracking",
    description: "Complete 3 meals a day for 7 days. Simple, honest tracking of your food journey.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: FileText,
    title: "Food Awareness Report",
    description: "Personalized observations about your eating patterns — educational, not judgmental.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: Award,
    title: "Wholesome Plate Education",
    description: "Learn the principles of balanced Indian eating through your own food data.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: ShieldCheck,
    title: "Traditional Foods Respected",
    description: "Idli, sambar, dal rice, ragi — Indian traditional foods are recognized as wholesome.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
];

export function Features() {
  return (
    <section className="py-24 px-4 bg-warm-gradient">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-primary font-semibold font-body text-sm uppercase tracking-widest">What You Get</span>
          <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mt-3 mb-4">
            A Different Kind of Food Journey
          </h2>
          <p className="text-dark/60 font-body text-lg max-w-xl mx-auto">
            Built around awareness and education, not numbers and restrictions.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="group bg-card rounded-2xl p-6 border border-border/50 shadow-soft hover:shadow-card hover:-translate-y-1 transition-all duration-300 cursor-default"
            >
              <div className={`w-12 h-12 rounded-xl ${f.bg} flex items-center justify-center mb-4`}>
                <f.icon className={`w-5 h-5 ${f.color}`} />
              </div>
              <h3 className="font-heading text-lg font-semibold text-dark mb-2">{f.title}</h3>
              <p className="font-body text-dark/60 text-sm leading-relaxed">{f.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
