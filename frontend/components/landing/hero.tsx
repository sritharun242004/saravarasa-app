"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Camera, Brain, ClipboardList } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-4 pt-20">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(27,96,64,0.08)_0%,transparent_70%)]" />

      <div className="relative z-10 max-w-3xl mx-auto text-center">
        {/* Hero Text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 bg-primary/10 text-primary border border-primary/20 rounded-full px-4 py-1.5 text-sm font-semibold font-body mb-6">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            Your Personalized Food Transformation
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold text-dark leading-[1.1] mb-6"
        >
          Understand Your{" "}
          <span className="text-primary relative">
            Food Patterns
            <svg className="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 300 8" preserveAspectRatio="none">
              <path d="M0 6 Q75 0 150 4 Q225 8 300 2" stroke="#1B6040" strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.4" />
            </svg>
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg sm:text-xl text-dark/60 font-body mb-10 max-w-2xl mx-auto leading-relaxed"
        >
          A simple 3-stage journey: Track your meals → Get AI insights → Unlock personalized recommendations. No restrictions, no calorie counting—just real food, real data.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <Link href="/signup">
            <Button size="xl" className="w-full sm:w-auto group bg-primary hover:bg-primary/90">
              🎯 Start 7-Day Challenge
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
          <Button
            size="xl"
            variant="outline"
            className="w-full sm:w-auto group"
            onClick={() => document.getElementById("journey")?.scrollIntoView({ behavior: "smooth" })}
          >
            See The Journey
          </Button>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex items-center justify-center gap-8 sm:gap-12 text-sm text-dark/50 font-body"
        >
          {[
            { value: "7", label: "Days" },
            { value: "3", label: "Stages" },
            { value: "Free", label: "No Cost" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold font-heading text-primary">{stat.value}</div>
              <div className="text-xs mt-0.5">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="w-6 h-10 border-2 border-primary/30 rounded-full flex items-start justify-center p-1.5"
        >
          <div className="w-1.5 h-1.5 bg-primary rounded-full" />
        </motion.div>
      </div>
    </section>
  );
}
