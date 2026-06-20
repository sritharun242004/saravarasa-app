"use client";

import { motion } from "framer-motion";

export function AnalyzingStep() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="text-center py-16"
    >
      <div className="relative w-24 h-24 mx-auto mb-8">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-full border-4 border-primary/20 border-t-primary"
        />
        <div className="absolute inset-3 bg-primary/10 rounded-full flex items-center justify-center">
          <span className="text-2xl">🍛</span>
        </div>
      </div>

      <h2 className="font-heading text-2xl font-bold text-dark mb-3">Analyzing Your Meal</h2>
      <p className="font-body text-dark/60 mb-8">Gemini Vision AI is identifying your food...</p>

      <div className="max-w-xs mx-auto space-y-3">
        {["Detecting dish type", "Identifying ingredients", "Matching INDB database"].map((step, i) => (
          <motion.div
            key={step}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.6, duration: 0.4 }}
            className="flex items-center gap-3 bg-card rounded-xl px-4 py-3 border border-border/50"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity, delay: i * 0.6 }}
              className="w-2 h-2 rounded-full bg-primary"
            />
            <span className="font-body text-sm text-dark/70">{step}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
