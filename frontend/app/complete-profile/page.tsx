"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { getProfile, updateProfile } from "@/lib/api";
import { Loader2, ArrowRight, User, Mail, Phone } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";

const fieldCls =
  "w-full pl-11 pr-5 h-12 rounded-full border border-border bg-white/60 font-body text-sm text-dark placeholder:text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus:border-accent transition";

function CompleteProfileInner() {
  const router = useRouter();
  const params = useSearchParams();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", phone: "" });

  const next = params.get("next") || "/challenge";
  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) {
      router.push("/login");
      return;
    }
    getProfile(clientId)
      .then((p) =>
        setForm({
          name: p.name || localStorage.getItem(CLIENT_NAME_KEY) || "",
          email: p.email || "",
          phone: p.phone || "",
        }),
      )
      .catch(() =>
        setForm((f) => ({ ...f, name: localStorage.getItem(CLIENT_NAME_KEY) || f.name })),
      )
      .finally(() => setLoading(false));
  }, [clientId, router]);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));
  const setPhone = (v: string) => set("phone", v.replace(/\D/g, "").slice(0, 10));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.phone.trim()) {
      toast({ title: "Please fill name, email and phone", variant: "destructive" });
      return;
    }
    if (!/^[6-9]\d{9}$/.test(form.phone)) {
      toast({ title: "Invalid phone", description: "Enter a valid 10-digit mobile number.", variant: "destructive" });
      return;
    }
    setSaving(true);
    try {
      const updated = await updateProfile(clientId, {
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
      });
      localStorage.setItem(CLIENT_NAME_KEY, updated.name || form.name);
      toast({ title: "All set!", description: "Your details have been saved." });
      router.push(next);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Could not save your details. Please try again.";
      toast({ title: "Error", description: msg, variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden">
        <div className="absolute -top-10 -left-16 w-80 h-80 bg-primary/10 blur-3xl blob-1 pointer-events-none" />
        <div className="absolute bottom-0 -right-16 w-80 h-80 bg-secondary/10 blur-3xl blob-2 pointer-events-none" />

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <User className="w-7 h-7 text-primary" />
            </div>
            <h1 className="font-heading text-3xl font-bold text-dark mb-2">A Few Details</h1>
            <p className="font-body text-muted-foreground">
              Confirm your details so we can personalise your journey.
            </p>
          </div>

          <Card className="shadow-float">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Full Name <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
                    <input value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Your full name" required className={fieldCls} />
                  </div>
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
                    <input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="you@example.com" required className={fieldCls} />
                  </div>
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Phone <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2" />
                    <input type="tel" inputMode="numeric" maxLength={10} value={form.phone} onChange={(e) => setPhone(e.target.value)} placeholder="10-digit mobile number" required className={fieldCls} />
                  </div>
                </div>

                <Button type="submit" disabled={saving} size="lg" className="w-full">
                  {saving ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving…</>
                  ) : (
                    <>Continue <ArrowRight className="w-4 h-4 ml-2" /></>
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

export default function CompleteProfilePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      }
    >
      <CompleteProfileInner />
    </Suspense>
  );
}
