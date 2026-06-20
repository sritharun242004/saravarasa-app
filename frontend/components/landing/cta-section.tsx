"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-24 px-4">
      <div className="max-w-3xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-card rounded-3xl p-12 border border-primary/20 shadow-elevated relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-48 h-48 bg-primary/5 rounded-full -translate-x-24 -translate-y-24" />
          <div className="absolute bottom-0 right-0 w-48 h-48 bg-accent/5 rounded-full translate-x-24 translate-y-24" />

          <div className="relative">
            <div className="w-16 h-16 bg-primary/10 border border-primary/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">🌿</span>
            </div>
            <h2 className="font-heading text-4xl sm:text-5xl font-bold text-dark mb-4">
              Begin Your Food Journey
            </h2>
            <p className="font-body text-dark/60 text-lg mb-8 max-w-md mx-auto">
              Start with a Lifestyle Audit and take the 7-Day Wholesome Eating Challenge.
              No special foods. No diets. Just awareness.
            </p>
            <Link href="/audit">
              <Button size="xl" className="group">
                Start Free Challenge
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <p className="font-body text-dark/40 text-sm mt-4">
              Completely free • Takes 5 minutes to start
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
