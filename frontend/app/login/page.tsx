"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { login } from "@/lib/api";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { isCognitoConfigured } from "@/lib/cognito";
import { Loader2, ArrowRight, Eye, EyeOff } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";
const ADMIN_TOKEN_KEY = "sarvarasa_admin_token";

const inputCls =
  "w-full px-5 h-12 rounded-full border border-border bg-white/60 font-body text-sm text-dark placeholder:text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus:border-accent transition";

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });

  const set = (key: string, val: string) => setForm((f) => ({ ...f, [key]: val }));

  useEffect(() => {
    if (localStorage.getItem(ADMIN_TOKEN_KEY)) router.replace("/admin");
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email.trim() || !form.password) {
      toast({ title: "Email and password are required", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      const res = await login(form.email, form.password);
      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);
      if (res.token) localStorage.setItem(TOKEN_KEY, res.token);

      toast({ title: "Welcome back!" });
      router.push("/profile");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Login failed. Check your email and password.";
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
            <h1 className="font-heading text-4xl font-bold text-dark mb-2">Welcome Back</h1>
            <p className="font-body text-muted-foreground">Log in to continue your wellness journey</p>
          </div>

          <Card className="shadow-float">
            <CardContent className="p-8">
              {isCognitoConfigured() && (
                <>
                  <GoogleSignInButton label="Log in with Google" />
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

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Password <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showPw ? "text" : "password"}
                      value={form.password}
                      onChange={(e) => set("password", e.target.value)}
                      placeholder="••••••••"
                      required
                      className={`${inputCls} pr-12`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPw((s) => !s)}
                      aria-label={showPw ? "Hide password" : "Show password"}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-dark"
                    >
                      {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  size="lg"
                  className="w-full"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Logging in…</>
                  ) : (
                    <>Log In <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="text-center font-body text-sm text-muted-foreground mt-6">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-primary font-bold hover:underline underline-offset-4">
              Sign up
            </Link>
          </p>
        </motion.div>
      </div>
    </AppShell>
  );
}
