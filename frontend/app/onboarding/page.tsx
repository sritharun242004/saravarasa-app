"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { registerClient } from "@/lib/api";
import { Loader2, ArrowRight } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";

export default function OnboardingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [form, setForm] = useState({ name: "", email: "", phone: "", age: "", gender: "" });
  const [loading, setLoading] = useState(false);

  const set = (key: string, val: string) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) {
      toast({ title: "Required", description: "Name and email are required.", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      const res = await registerClient({
        name: form.name,
        email: form.email,
        phone: form.phone || undefined,
        age: form.age ? parseInt(form.age) : undefined,
        gender: form.gender || undefined,
      });
      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);
      toast({ title: "Welcome!", description: "Let's start the 7-Day Challenge!" });
      router.push("/challenge");
    } catch {
      toast({ title: "Error", description: "Registration failed. Please try again.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-lg mx-auto px-4 py-16">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🌿</span>
            </div>
            <h1 className="font-heading text-3xl font-bold text-dark mb-2">Join the Challenge</h1>
            <p className="font-body text-dark/60">
              Create your Sarvarasa account to start the 7-Day Wholesome Eating Challenge.
            </p>
          </div>

          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-1.5">
                    Full Name <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => set("name", e.target.value)}
                    placeholder="Your full name"
                    required
                    className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-1.5">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-1.5">Phone (optional)</label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => set("phone", e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-body text-sm font-medium text-dark mb-1.5">Age (optional)</label>
                    <input
                      type="number"
                      value={form.age}
                      onChange={(e) => set("age", e.target.value)}
                      placeholder="28"
                      min={10}
                      max={99}
                      className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block font-body text-sm font-medium text-dark mb-1.5">Gender (optional)</label>
                    <select
                      value={form.gender}
                      onChange={(e) => set("gender", e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                    >
                      <option value="">Select</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <Button type="submit" disabled={loading} size="lg" className="w-full">
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Registering…</>
                  ) : (
                    <>Start Challenge <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AppShell>
  );
}
