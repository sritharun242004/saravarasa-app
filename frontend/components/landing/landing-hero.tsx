"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function LandingHero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-4 sm:px-6 pt-28 pb-20">
      {/* Ambient organic blobs */}
      <div className="absolute -top-20 -left-24 w-[28rem] h-[28rem] bg-primary/15 blur-3xl blob-1 pointer-events-none" />
      <div className="absolute top-1/3 -right-28 w-[26rem] h-[26rem] bg-secondary/15 blur-3xl blob-2 pointer-events-none" />
      <div className="absolute -bottom-24 left-1/4 w-[22rem] h-[22rem] bg-accent/15 blur-3xl blob-3 pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold text-dark leading-[1.08] mb-6 text-balance"
        >
          Understand Your Eating,
          <span className="text-primary"> Transform Your Health</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg sm:text-xl text-muted-foreground font-body mb-10 max-w-2xl mx-auto leading-relaxed text-balance"
        >
          Complete a 7-day food challenge, a lifestyle audit, and a descriptive test, all inside the app,
          to discover your patterns and get personalised, science-backed guidance.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-7"
        >
          <Link href="/signup" className="w-full sm:w-auto">
            <Button size="lg" className="w-full sm:w-auto">
              Get Started, Sign Up
              <ArrowRight className="w-5 h-5 ml-1" />
            </Button>
          </Link>
          <Button
            size="lg"
            variant="outline"
            className="w-full sm:w-auto"
            onClick={() => document.getElementById("assessments")?.scrollIntoView({ behavior: "smooth" })}
          >
            Explore the Assessments
          </Button>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="font-body text-sm text-muted-foreground"
        >
          Already have an account?{" "}
          <Link href="/login" className="text-primary font-bold hover:underline underline-offset-4">
            Log in
          </Link>
        </motion.p>
      </div>
    </section>
  );
}
