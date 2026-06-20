"use client";

import { motion } from "framer-motion";
import { Camera, Brain, ClipboardList, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const stages = [
  {
    number: 1,
    title: "7-Day Food Challenge",
    subtitle: "Track & Upload",
    description: "Submit photos of your meals for 7 consecutive days. Breakfast, lunch, dinner—just take a pic and upload. No restrictions, eat what you normally eat.",
    icon: Camera,
    color: "bg-primary/10 border-primary/30",
    benefits: [
      "Capture your real eating habits",
      "Build awareness of your patterns",
      "Generate personalized food data",
    ],
  },
  {
    number: 2,
    title: "AI Food Analysis",
    subtitle: "Get Insights",
    description: "Our AI analyzes 7 days of meal data to understand your food patterns, nutritional gaps, and eating behaviors.",
    icon: Brain,
    color: "bg-secondary/10 border-secondary/30",
    benefits: [
      "Pattern recognition from your meals",
      "Nutritional gap analysis",
      "Personalized food recommendations",
    ],
  },
  {
    number: 3,
    title: "Lifestyle & Insights",
    subtitle: "Deep Understanding",
    description: "Complete the lifestyle audit and descriptive questions to get a full picture of your health and personalized action plan.",
    icon: ClipboardList,
    color: "bg-primary/5 border-primary/20",
    benefits: [
      "Lifestyle context understanding",
      "Stress & digestion patterns",
      "Complete wellness roadmap",
    ],
  },
];

export function JourneyStages() {
  return (
    <section id="journey" className="relative py-24 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <span className="text-primary font-semibold text-sm uppercase tracking-widest">THE JOURNEY</span>
          <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mt-3 mb-4">
            Your 3-Stage Transformation
          </h2>
          <p className="text-dark/60 text-lg max-w-2xl mx-auto font-body">
            A simple, structured path from food awareness to personalized wellness recommendations.
          </p>
        </motion.div>

        {/* Stages Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {stages.map((stage, idx) => {
            const IconComponent = stage.icon;
            const isLast = idx === stages.length - 1;

            return (
              <motion.div
                key={stage.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: idx * 0.2 }}
                viewport={{ once: true }}
                className="relative"
              >
                {/* Connector line */}
                {!isLast && (
                  <div className="hidden md:block absolute top-24 -right-3 w-6 h-0.5 bg-gradient-to-r from-primary/30 to-transparent" />
                )}

                <Card className={`h-full border-2 ${stage.color}`}>
                  <CardContent className="p-8">
                    {/* Stage Number Badge */}
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                      <span className="font-heading text-xl font-bold text-primary">
                        {stage.number}
                      </span>
                    </div>

                    {/* Icon */}
                    <IconComponent className="w-10 h-10 text-primary mb-4" />

                    {/* Title */}
                    <h3 className="font-heading text-xl font-bold text-dark mb-1">
                      {stage.title}
                    </h3>
                    <p className="text-primary font-semibold text-sm mb-4">
                      {stage.subtitle}
                    </p>

                    {/* Description */}
                    <p className="font-body text-dark/70 text-sm mb-6 leading-relaxed">
                      {stage.description}
                    </p>

                    {/* Benefits */}
                    <ul className="space-y-2">
                      {stage.benefits.map((benefit, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm font-body text-dark/60">
                          <span className="text-secondary font-bold mt-0.5">✓</span>
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Flow Diagram for Mobile */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="md:hidden flex flex-col items-center gap-3 mt-12"
        >
          {stages.map((stage, idx) => (
            <div key={stage.number}>
              <div className="text-center text-sm font-body text-primary font-semibold">
                Stage {stage.number}: {stage.title}
              </div>
              {idx < stages.length - 1 && (
                <div className="w-0.5 h-4 bg-primary/20 mx-auto mt-3" />
              )}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
