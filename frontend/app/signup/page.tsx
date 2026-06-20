"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { signup } from "@/lib/api";
import { Loader2, ArrowRight, Eye, EyeOff, Lock } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block font-body text-sm font-medium text-dark mb-1.5">
        {label} {required && <span className="text-destructive">*</span>}
      </label>
      {children}
    </div>
  );
}

const inputCls =
  "w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary";

export default function SignupPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm: "",
    phone: "",
    age: "",
    gender: "",
    goal: "",
  });

  const set = (key: string, val: string) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.password) {
      toast({ title: "Required fields missing", variant: "destructive" });
      return;
    }
    if (form.password.length < 6) {
      toast({ title: "Password too short", description: "Minimum 6 characters.", variant: "destructive" });
      return;
    }
    if (form.password !== form.confirm) {
      toast({ title: "Passwords don't match", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      const res = await signup({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined,
        age: form.age ? parseInt(form.age) : undefined,
        gender: form.gender || undefined,
        goal: form.goal || undefined,
      });

      localStorage.setItem(TOKEN_KEY, res.token);
      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);

      toast({ title: "Account created!", description: "Let's start the 7-Day Challenge!" });
      router.push("/challenge");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Signup failed. Please try again.";
      toast({ title: "Error", description: msg, variant: "destructive" });
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
            <h1 className="font-heading text-3xl font-bold text-dark mb-2">Create Account</h1>
            <p className="font-body text-dark/60">
              Join the 7-Day Wholesome Eating Challenge
            </p>
          </div>

          {/* Milestones */}
          <div className="mb-8 grid grid-cols-3 gap-3">
            {/* Phase 1: 7-Day Challenge */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-primary/10 border-2 border-primary rounded-xl p-4 text-center"
            >
              <div className="flex items-center justify-center mb-2">
                <span className="text-2xl">📸</span>
              </div>
              <h3 className="font-body font-semibold text-sm text-dark mb-1">Phase 1</h3>
              <p className="font-body text-xs text-dark/70">7-Day Challenge</p>
              <p className="font-body text-xs text-primary font-medium mt-1">Active</p>
            </motion.div>

            {/* Phase 2: Audit */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-dark/5 border-2 border-dark/20 rounded-xl p-4 text-center opacity-60"
            >
              <div className="flex items-center justify-center mb-2">
                <Lock className="w-6 h-6 text-dark/40" />
              </div>
              <h3 className="font-body font-semibold text-sm text-dark mb-1">Phase 2</h3>
              <p className="font-body text-xs text-dark/70">Lifestyle Audit</p>
              <p className="font-body text-xs text-dark/40 mt-1">Locked</p>
            </motion.div>

            {/* Phase 3: Questions */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-dark/5 border-2 border-dark/20 rounded-xl p-4 text-center opacity-60"
            >
              <div className="flex items-center justify-center mb-2">
                <Lock className="w-6 h-6 text-dark/40" />
              </div>
              <h3 className="font-body font-semibold text-sm text-dark mb-1">Phase 3</h3>
              <p className="font-body text-xs text-dark/70">Deep Insights</p>
              <p className="font-body text-xs text-dark/40 mt-1">Locked</p>
            </motion.div>
          </div>

          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <Field label="Full Name" required>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => set("name", e.target.value)}
                    placeholder="Your full name"
                    required
                    className={inputCls}
                  />
                </Field>

                <Field label="Email" required>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    placeholder="you@gmail.com"
                    required
                    className={inputCls}
                  />
                </Field>

                <Field label="Password" required>
                  <div className="relative">
                    <input
                      type={showPw ? "text" : "password"}
                      value={form.password}
                      onChange={(e) => set("password", e.target.value)}
                      placeholder="Min. 6 characters"
                      required
                      className={inputCls + " pr-11"}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPw((v) => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-dark/40 hover:text-dark"
                    >
                      {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </Field>

                <Field label="Confirm Password" required>
                  <input
                    type="password"
                    value={form.confirm}
                    onChange={(e) => set("confirm", e.target.value)}
                    placeholder="Re-enter password"
                    required
                    className={inputCls}
                  />
                </Field>

                <Field label="Phone (optional)">
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => set("phone", e.target.value)}
                    placeholder="+91 98765 43210"
                    className={inputCls}
                  />
                </Field>

                <div className="grid grid-cols-2 gap-3">
                  <Field label="Age (optional)">
                    <input
                      type="number"
                      value={form.age}
                      onChange={(e) => set("age", e.target.value)}
                      placeholder="28"
                      min={10}
                      max={99}
                      className={inputCls}
                    />
                  </Field>
                  <Field label="Gender (optional)">
                    <select
                      value={form.gender}
                      onChange={(e) => set("gender", e.target.value)}
                      className={inputCls}
                    >
                      <option value="">Select</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </Field>
                </div>

                <Field label="Health Goal (optional)">
                  <select
                    value={form.goal}
                    onChange={(e) => set("goal", e.target.value)}
                    className={inputCls}
                  >
                    <option value="">Select a goal</option>
                    <option value="weight_loss">Weight Loss</option>
                    <option value="muscle_gain">Muscle Gain</option>
                    <option value="better_nutrition">Better Nutrition</option>
                    <option value="energy">More Energy</option>
                    <option value="general_health">General Health</option>
                  </select>
                </Field>

                <Button type="submit" disabled={loading} size="lg" className="w-full bg-primary hover:bg-primary/90">
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Starting challenge…</>
                  ) : (
                    <>🎯 Take 7-Day Challenge <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>

                <p className="text-center font-body text-sm text-dark/60">
                  Already have an account?{" "}
                  <Link href="/login" className="text-primary font-medium hover:underline">
                    Log in
                  </Link>
                </p>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AppShell>
  );
}
