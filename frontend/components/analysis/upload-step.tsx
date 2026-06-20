"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import Image from "next/image";
import { Camera, Upload, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { analyzeImage, type AnalyzeImageResponse } from "@/lib/api";
import { toast } from "@/lib/use-toast";
import { cn } from "@/lib/utils";

interface Props {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: AnalyzeImageResponse) => void;
}

export function UploadStep({ onAnalysisStart, onAnalysisComplete }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0];
    if (!f) return;
    setFile(f);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp", ".heic"] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    onAnalysisStart();
    try {
      const result = await analyzeImage(file);
      onAnalysisComplete(result);
    } catch {
      toast({ title: "Analysis failed", description: "Please try again with a clearer photo.", variant: "destructive" });
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
    >
      {!preview ? (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-200 cursor-pointer",
            isDragActive
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border hover:border-primary/50 hover:bg-muted/50"
          )}
        >
          <input {...getInputProps()} />
          <div className="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
            {isDragActive ? (
              <Upload className="w-8 h-8 text-primary" />
            ) : (
              <Camera className="w-8 h-8 text-primary" />
            )}
          </div>
          <h3 className="font-heading text-xl font-semibold text-dark mb-2">
            {isDragActive ? "Drop your photo here" : "Upload Food Photo"}
          </h3>
          <p className="font-body text-dark/60 mb-6">
            Take a photo or drag & drop from gallery
          </p>
          <Button variant="outline" size="lg" type="button">
            <Upload className="w-4 h-4" />
            Choose Photo
          </Button>
          <p className="font-body text-xs text-dark/40 mt-4">
            JPG, PNG, WEBP, HEIC up to 10MB
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="relative rounded-3xl overflow-hidden aspect-[4/3] bg-muted">
            <Image
              src={preview}
              alt="Food preview"
              fill
              className="object-cover"
            />
            <button
              onClick={() => { setPreview(null); setFile(null); }}
              className="absolute top-3 right-3 w-9 h-9 bg-dark/60 rounded-full flex items-center justify-center hover:bg-dark/80 transition-colors cursor-pointer"
              aria-label="Remove image"
            >
              <X className="w-4 h-4 text-white" />
            </button>
          </div>

          <div className="bg-card rounded-2xl p-4 border border-border/50">
            <p className="font-body text-sm text-dark/60 mb-1">Selected file</p>
            <p className="font-body text-dark font-medium truncate">{file?.name}</p>
          </div>

          <Button
            size="lg"
            className="w-full"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze This Meal"
            )}
          </Button>
        </div>
      )}
    </motion.div>
  );
}
