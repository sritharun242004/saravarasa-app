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
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { isCognitoConfigured } from "@/lib/cognito";
import { Loader2, ArrowRight, Eye, EyeOff } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[6-9]\d{9}$/;

const inputCls =
  "w-full px-5 h-12 rounded-full border border-border bg-white/60 font-body text-sm text-dark placeholder:text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus:border-accent transition";

type Errors = Partial<Record<"name" | "email" | "phone" | "password" | "confirm", string>>;

export default function SignupPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [errors, setErrors] = useState<Errors>({});
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirm: "",
    age: "",
    gender: "",
  });

  // Update a field and clear its error so the highlight disappears as the user fixes it.
  const set = (key: string, val: string) => {
    setForm((f) => ({ ...f, [key]: val }));
    setErrors((e) => (e[key as keyof Errors] ? { ...e, [key]: undefined } : e));
  };

  // Keep phone to digits only, max 10.
  const setPhone = (val: string) => set("phone", val.replace(/\D/g, "").slice(0, 10));

  // Input classes — add a red highlight when the field has an error.
  const cls = (field: keyof Errors, extra = "") =>
    `${inputCls} ${extra} ${
      errors[field]
        ? "border-destructive focus-visible:ring-destructive/30 focus:border-destructive"
        : ""
    }`;

  const validateFields = (): Errors => {
    const e: Errors = {};
    if (form.name.trim().length < 2) e.name = "Please enter your full name.";
    if (!EMAIL_RE.test(form.email.trim())) e.email = "Enter a valid email address.";
    if (!PHONE_RE.test(form.phone)) e.phone = "Enter a valid 10-digit mobile number.";
    if (form.password.length < 8) e.password = "Password must be at least 8 characters.";
    else if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password))
      e.password = "Include at least one letter and one number.";
    if (!form.confirm || form.password !== form.confirm) e.confirm = "Passwords do not match.";
    return e;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const found = validateFields();
    if (Object.keys(found).length > 0) {
      setErrors(found);
      // Focus the first field with an error so the user lands right on it.
      const first = (["name", "email", "phone", "password", "confirm"] as const).find((f) => found[f]);
      if (first) document.getElementById(`signup-${first}`)?.focus();
      return;
    }
    setErrors({});

    setLoading(true);
    try {
      const res = await signup({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone: form.phone,
        age: form.age ? parseInt(form.age) : undefined,
        gender: form.gender || undefined,
      });

      localStorage.setItem(CLIENT_ID_KEY, res.client_id);
      localStorage.setItem(CLIENT_NAME_KEY, res.name);
      if (res.token) localStorage.setItem(TOKEN_KEY, res.token);

      toast({ title: "Welcome!", description: "Let's start the 7-Day Challenge!" });
      router.push("/challenge");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Signup failed. Please try again.";
      // Map server errors to the right field so it gets highlighted.
      if (status === 409 || /email/i.test(msg)) {
        setErrors((e) => ({ ...e, email: msg }));
        document.getElementById("signup-email")?.focus();
      } else if (/phone|mobile/i.test(msg)) {
        setErrors((e) => ({ ...e, phone: msg }));
        document.getElementById("signup-phone")?.focus();
      } else if (/password/i.test(msg)) {
        setErrors((e) => ({ ...e, password: msg }));
        document.getElementById("signup-password")?.focus();
      } else {
        toast({ title: "Error", description: msg, variant: "destructive" });
      }
    } finally {
      setLoading(false);
    }
  };

  const ErrMsg = ({ field }: { field: keyof Errors }) =>
    errors[field] ? (
      <p className="font-body text-xs text-destructive mt-1.5 px-1">{errors[field]}</p>
    ) : null;

  return (
    <AppShell>
      <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden">
        <div className="absolute -top-10 -left-16 w-80 h-80 bg-primary/10 blur-3xl blob-1 pointer-events-none" />
        <div className="absolute bottom-0 -right-16 w-80 h-80 bg-secondary/10 blur-3xl blob-2 pointer-events-none" />
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="font-heading text-4xl font-bold text-dark mb-2">Create Your Account</h1>
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

              <form onSubmit={handleSubmit} className="space-y-5" noValidate>
                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Full Name <span className="text-destructive">*</span>
                  </label>
                  <input
                    id="signup-name"
                    type="text"
                    value={form.name}
                    onChange={(e) => set("name", e.target.value)}
                    placeholder="John Doe"
                    autoComplete="name"
                    aria-invalid={!!errors.name}
                    required
                    className={cls("name")}
                  />
                  <ErrMsg field="name" />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <input
                    id="signup-email"
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    placeholder="you@example.com"
                    autoComplete="email"
                    aria-invalid={!!errors.email}
                    required
                    className={cls("email")}
                  />
                  <ErrMsg field="email" />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Phone <span className="text-destructive">*</span>
                  </label>
                  <div className="relative flex items-center">
                    <span className="absolute left-5 font-body text-sm text-muted-foreground pointer-events-none">+91</span>
                    <input
                      id="signup-phone"
                      type="tel"
                      inputMode="numeric"
                      value={form.phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="98765 43210"
                      autoComplete="tel"
                      maxLength={10}
                      aria-invalid={!!errors.phone}
                      required
                      className={cls("phone", "pl-14")}
                    />
                  </div>
                  <ErrMsg field="phone" />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Password <span className="text-destructive">*</span>
                  </label>
                  <div className="relative">
                    <input
                      id="signup-password"
                      type={showPw ? "text" : "password"}
                      value={form.password}
                      onChange={(e) => set("password", e.target.value)}
                      placeholder="Min 8 chars, 1 letter & 1 number"
                      autoComplete="new-password"
                      aria-invalid={!!errors.password}
                      required
                      className={cls("password", "pr-12")}
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
                  <ErrMsg field="password" />
                </div>

                <div>
                  <label className="block font-body text-sm font-medium text-dark mb-2">
                    Confirm Password <span className="text-destructive">*</span>
                  </label>
                  <input
                    id="signup-confirm"
                    type={showPw ? "text" : "password"}
                    value={form.confirm}
                    onChange={(e) => set("confirm", e.target.value)}
                    placeholder="Re-enter your password"
                    autoComplete="new-password"
                    aria-invalid={!!errors.confirm}
                    required
                    className={cls("confirm")}
                  />
                  <ErrMsg field="confirm" />
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

                <Button type="submit" disabled={loading} size="lg" className="w-full">
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Creating account…</>
                  ) : (
                    <>Create Account <ArrowRight className="w-4 h-4 ml-2" /></>
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
          <p className="text-center font-body text-xs text-muted-foreground/70 mt-2">
            By signing up, you agree to start your wellness journey with us.
          </p>
        </motion.div>
      </div>
    </AppShell>
  );
}
