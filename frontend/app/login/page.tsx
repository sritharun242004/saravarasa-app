"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { login } from "@/lib/api";
import { Loader2, ArrowRight, Eye, EyeOff } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";

const inputCls =
  "w-full px-4 py-3 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary";

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      toast({ title: "Email and password are required", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      const res = await login(email, password);

      localStorage.setItem(TOKEN_KEY, res.token);
      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);

      toast({ title: `Welcome back, ${res.name}!` });
      router.push("/challenge");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Invalid email or password.";
      toast({ title: "Login failed", description: msg, variant: "destructive" });
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
            <h1 className="font-heading text-3xl font-bold text-dark mb-2">Welcome Back</h1>
            <p className="font-body text-dark/60">Log in to continue your challenge</p>
          </div>

          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-1.5">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@gmail.com"
                    required
                    autoFocus
                    className={inputCls}
                  />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-1.5">
                    Password <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showPw ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Your password"
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
                </div>

                <Button type="submit" disabled={loading} size="lg" className="w-full">
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Logging in…</>
                  ) : (
                    <>Log In <ArrowRight className="w-4 h-4 ml-2" /></>
                  )}
                </Button>

                <p className="text-center font-body text-sm text-dark/60">
                  Don&apos;t have an account?{" "}
                  <Link href="/signup" className="text-primary font-medium hover:underline">
                    Sign up free
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
