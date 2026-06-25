"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { adminLogin } from "@/lib/api";
import { Loader2, ArrowRight, ShieldCheck, Mail, Lock } from "lucide-react";

const ADMIN_TOKEN_KEY = "sarvarasa_admin_token";
const ADMIN_EMAIL_KEY = "sarvarasa_admin_email";

const fieldCls =
  "w-full pl-11 pr-5 h-12 rounded-full border border-border bg-white/60 font-body text-sm text-dark placeholder:text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus:border-accent transition";

export default function AdminLoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email.trim() || !form.password) {
      toast({ title: "Email and password are required", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      const res = await adminLogin(form.email.trim(), form.password);
      localStorage.setItem(ADMIN_TOKEN_KEY, res.token);
      localStorage.setItem(ADMIN_EMAIL_KEY, res.email);
      toast({ title: "Welcome, admin" });
      router.push("/admin");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Invalid admin credentials.";
      toast({ title: "Login failed", description: msg, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden bg-background">
      <div className="absolute -top-10 -left-16 w-80 h-80 bg-primary/10 blur-3xl blob-1 pointer-events-none" />
      <div className="absolute bottom-0 -right-16 w-80 h-80 bg-secondary/10 blur-3xl blob-2 pointer-events-none" />

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <ShieldCheck className="w-7 h-7 text-primary" />
          </div>
          <h1 className="font-heading text-3xl font-bold text-dark mb-2">Admin Console</h1>
          <p className="font-body text-muted-foreground">Restricted access. Sign in to continue.</p>
        </div>

        <Card className="shadow-float">
          <CardContent className="p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block font-body text-sm font-medium text-dark mb-2">
                  Admin Email <span className="text-destructive">*</span>
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
                  <input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="admin@example.com" required className={fieldCls} />
                </div>
              </div>

              <div>
                <label className="block font-body text-sm font-medium text-dark mb-2">
                  Password <span className="text-destructive">*</span>
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
                  <input type="password" value={form.password} onChange={(e) => set("password", e.target.value)} placeholder="••••••••" required className={fieldCls} />
                </div>
              </div>

              <Button type="submit" disabled={loading} size="lg" className="w-full">
                {loading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Signing in…</>
                ) : (
                  <>Sign In <ArrowRight className="w-4 h-4 ml-2" /></>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
