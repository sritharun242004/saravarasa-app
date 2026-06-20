"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, PenLine } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { UploadStep } from "@/components/analysis/upload-step";
import { ManualInputStep } from "@/components/analysis/manual-input-step";
import { QuestionsStep } from "@/components/analysis/questions-step";
import { AnalyzingStep } from "@/components/analysis/analyzing-step";
import { cn } from "@/lib/utils";
import type { AnalyzeImageResponse, QuestionsResponse } from "@/lib/api";

type Step = "upload" | "analyzing" | "questions" | "calculating";
type InputMode = "photo" | "manual";

export default function AnalyzePage() {
  const [step, setStep] = useState<Step>("upload");
  const [inputMode, setInputMode] = useState<InputMode>("photo");
  const [analysisResult, setAnalysisResult] = useState<AnalyzeImageResponse | null>(null);
  const [questionsResult, setQuestionsResult] = useState<QuestionsResponse | null>(null);

  const isInputStep = step === "upload";

  return (
    <AppShell>
      <div className="min-h-screen px-4 py-8 max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="font-heading text-3xl font-bold text-dark">Analyze Meal</h1>
          <p className="font-body text-dark/60 mt-1">
            {inputMode === "photo"
              ? "Upload a photo of your Indian food"
              : "Type the foods you ate manually"}
          </p>
        </motion.div>

        <StepIndicator step={step} />

        {/* Mode toggle — only visible on the input step */}
        <AnimatePresence>
          {isInputStep && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="flex rounded-2xl bg-muted p-1 mb-6"
            >
              <button
                type="button"
                onClick={() => setInputMode("photo")}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-body text-sm font-medium transition-all duration-200 cursor-pointer",
                  inputMode === "photo"
                    ? "bg-card text-dark shadow-soft"
                    : "text-dark/50 hover:text-dark/70"
                )}
              >
                <Camera className="w-4 h-4" />
                Photo
              </button>
              <button
                type="button"
                onClick={() => setInputMode("manual")}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-body text-sm font-medium transition-all duration-200 cursor-pointer",
                  inputMode === "manual"
                    ? "bg-card text-dark shadow-soft"
                    : "text-dark/50 hover:text-dark/70"
                )}
              >
                <PenLine className="w-4 h-4" />
                Manual
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {step === "upload" && inputMode === "photo" && (
            <UploadStep
              key="upload-photo"
              onAnalysisStart={() => setStep("analyzing")}
              onAnalysisComplete={(result) => {
                setAnalysisResult(result);
                setStep("questions");
              }}
            />
          )}
          {step === "upload" && inputMode === "manual" && (
            <ManualInputStep
              key="upload-manual"
              onAnalysisStart={() => setStep("analyzing")}
            />
          )}
          {step === "analyzing" && <AnalyzingStep key="analyzing" />}
          {step === "questions" && analysisResult && (
            <QuestionsStep
              key="questions"
              analysisResult={analysisResult}
              onComplete={(result) => {
                setQuestionsResult(result);
                setStep("calculating");
              }}
            />
          )}
          {step === "calculating" && analysisResult && questionsResult && (
            <CalculatingStep key="calculating" />
          )}
        </AnimatePresence>
      </div>
    </AppShell>
  );
}

function StepIndicator({ step }: { step: Step }) {
  const steps = ["upload", "analyzing", "questions", "calculating"];
  const current = steps.indexOf(step);

  return (
    <div className="flex items-center gap-2 mb-8">
      {steps.map((s, i) => (
        <div key={s} className="flex items-center gap-2 flex-1 last:flex-none">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold font-body transition-all duration-300 ${
              i <= current
                ? "bg-primary text-white"
                : "bg-muted text-dark/40"
            }`}
          >
            {i + 1}
          </div>
          {i < steps.length - 1 && (
            <div
              className={`h-0.5 flex-1 transition-all duration-300 ${
                i < current ? "bg-primary" : "bg-muted"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

function CalculatingStep() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="text-center py-16"
    >
      <div className="w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-6">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="w-10 h-10 border-3 border-accent border-t-transparent rounded-full"
          style={{ borderWidth: 3 }}
        />
      </div>
      <h2 className="font-heading text-2xl font-semibold text-dark mb-2">Calculating Nutrition</h2>
      <p className="font-body text-dark/60">Cross-referencing with INDB database...</p>
    </motion.div>
  );
}
