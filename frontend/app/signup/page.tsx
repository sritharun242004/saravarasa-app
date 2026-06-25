"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { registerClient } from "@/lib/api";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { isCognitoConfigured } from "@/lib/cognito";
import { Loader2, ArrowRight } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";

const inputCls =
  "w-full px-5 h-12 rounded-full border border-border bg-white/60 font-body text-sm text-dark placeholder:text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus:border-accent transition";

export default function SignupPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    age: "",
    gender: "",
    goal: "",
  });

  const set = (key: string, val: string) => setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim()) {
      toast({ title: "Name and email are required", variant: "destructive" });
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
        goal: form.goal || undefined,
      });

      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);

      toast({ title: "Welcome!", description: "Let's start the 7-Day Challenge!" });
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
      <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden">
        <div className="absolute -top-10 -left-16 w-80 h-80 bg-primary/10 blur-3xl blob-1 pointer-events-none" />
        <div className="absolute bottom-0 -right-16 w-80 h-80 bg-secondary/10 blur-3xl blob-2 pointer-events-none" />
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="font-heading text-4xl font-bold text-dark mb-2">Start Your Journey</h1>
            <p className="font-body text-muted-foreground">
              Join the 7-Day Wholesome Eating Challenge
            </p>
          </div>

          <Card className="shadow-float">
            <CardContent className="p-8">
              {isCognitoConfigured() && (
                <>
                  <GoogleSignInButton label="Sign up with Google" />
                  <div className="flex items-center gap-3 my-6">
                    <div className="h-px flex-1 bg-border" />
                    <span className="font-body text-xs text-muted-foreground uppercase tracking-widest">or</span>
                    <div className="h-px flex-1 bg-border" />
                  </div>
                </>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Full Name <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => set("name", e.target.value)}
                    placeholder="John Doe"
                    required
                    className={inputCls}
                  />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    placeholder="you@example.com"
                    required
                    className={inputCls}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-body text-sm font-medium text-dark mb-2">Age</label>
                    <input
                      type="number"
                      value={form.age}
                      onChange={(e) => set("age", e.target.value)}
                      placeholder="28"
                      min={10}
                      max={99}
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className="block font-body text-sm font-medium text-dark mb-2">Gender</label>
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
                  </div>
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">Phone</label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => set("phone", e.target.value)}
                    placeholder="+91 98765 43210"
                    className={inputCls}
                  />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">Health Goal</label>
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
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  size="lg"
                  className="w-full"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Starting…</>
                  ) : (
                    <>Begin Challenge <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="text-center font-body text-sm text-muted-foreground mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-primary font-bold hover:underline underline-offset-4">
              Log in
            </Link>
          </p>
          <p className="text-center font-body text-xs text-gray-400 mt-2">
            By signing up, you agree to start your wellness journey with us.
          </p>
        </motion.div>
      </div>
    </AppShell>
  );
}
