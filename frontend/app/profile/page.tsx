"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  getProfile,
  getChallengeProgress,
  getAuditResult,
  getTestStatus,
  type Profile,
  type ChallengeProgress,
  type AuditResult,
  type TestStatus,
} from "@/lib/api";
import {
  Loader2,
  Mail,
  Phone,
  User,
  Utensils,
  ClipboardList,
  PenTool,
  ArrowRight,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [progress, setProgress] = useState<ChallengeProgress | null>(null);
  const [audit, setAudit] = useState<AuditResult | null>(null);
  const [testStatus, setTestStatus] = useState<TestStatus | null>(null);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  useEffect(() => {
    if (!clientId) {
      router.push("/login");
      return;
    }
    Promise.allSettled([
      getProfile(clientId),
      getChallengeProgress(clientId),
      getAuditResult(clientId),
      getTestStatus(clientId),
    ])
      .then(([p, prog, aud, ts]) => {
        if (p.status === "fulfilled") setProfile(p.value);
        if (prog.status === "fulfilled") setProgress(prog.value);
        if (aud.status === "fulfilled") setAudit(aud.value);
        if (ts.status === "fulfilled") setTestStatus(ts.value);
      })
      .finally(() => setLoading(false));
  }, [clientId, router]);

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(CLIENT_ID_KEY);
    localStorage.removeItem(CLIENT_NAME_KEY);
    router.push("/");
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

  const name = profile?.name || localStorage.getItem(CLIENT_NAME_KEY) || "Your Profile";
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const compliancePct = progress?.compliance_pct ?? 0;
  const completedDays = progress?.completed_days ?? 0;
  const descriptiveDone = !!testStatus?.descriptive_completed;

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Identity header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
                  <span className="font-heading text-xl font-bold text-primary">{initials || "U"}</span>
                </div>
                <div className="min-w-0">
                  <h1 className="font-heading text-2xl font-bold text-dark truncate">{name}</h1>
                  <p className="font-body text-sm text-dark/50 truncate">{profile?.email || "—"}</p>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="ml-auto text-dark/60 hover:text-dark shrink-0"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4 mr-2" /> Logout
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Account details */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Account Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <DetailRow icon={<User className="w-4 h-4" />} label="Name" value={profile?.name} />
              <DetailRow icon={<Mail className="w-4 h-4" />} label="Email" value={profile?.email} />
              <DetailRow icon={<Phone className="w-4 h-4" />} label="Phone" value={profile?.phone} />
              {(profile?.age || profile?.gender) && (
                <DetailRow
                  icon={<User className="w-4 h-4" />}
                  label="Age / Gender"
                  value={[profile?.age, profile?.gender].filter(Boolean).join(" · ")}
                />
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* 3 phase results */}
        <div className="space-y-1">
          <h2 className="font-heading text-lg font-bold text-dark px-1">Your Journey</h2>
          <p className="font-body text-sm text-dark/50 px-1 pb-2">Results across all three phases.</p>
        </div>

        {/* Phase 1 — Challenge */}
        <PhaseCard
          delay={0.1}
          number={1}
          icon={<Utensils className="w-5 h-5 text-primary" />}
          title="7-Day Challenge"
          href="/challenge/progress"
          cta="Open Challenge"
        >
          {progress ? (
            <div className="space-y-3">
              <div className="flex items-end justify-between">
                <div>
                  <p className="font-heading text-3xl font-bold text-dark">{compliancePct}%</p>
                  <p className="font-body text-xs text-dark/50">{completedDays} of 7 days complete</p>
                </div>
                <Badge className={cn(
                  "text-xs",
                  compliancePct >= 85 ? "bg-accent/20 text-accent border-accent/30" : "bg-primary/15 text-primary border-primary/30"
                )}>
                  {compliancePct >= 85 ? "QUALIFIED" : (progress.status || "IN PROGRESS")}
                </Badge>
              </div>
              <Progress value={compliancePct} className="h-2" />
            </div>
          ) : (
            <EmptyHint text="No challenge activity yet. Start logging your meals." />
          )}
        </PhaseCard>

        {/* Phase 2 — Analysis */}
        <PhaseCard
          delay={0.15}
          number={2}
          icon={<ClipboardList className="w-5 h-5 text-primary" />}
          title="Lifestyle Audit"
          href="/audit"
          cta="Take the Audit"
        >
          {audit ? (
            <div className="space-y-3">
              <div className="flex items-end justify-between">
                <div>
                  <p className="font-heading text-3xl font-bold text-dark">
                    {audit.total_score}
                    <span className="text-base text-dark/40 font-body"> / {audit.max_score}</span>
                  </p>
                  <p className="font-body text-xs text-dark/50">Focus area: {audit.lowest_domain}</p>
                </div>
                <Badge className={cn(
                  "text-xs",
                  audit.zone === "Green" ? "bg-accent/20 text-accent border-accent/30" :
                  audit.zone === "Yellow" ? "bg-yellow-100 text-yellow-700 border-yellow-300" :
                  audit.zone === "Orange" ? "bg-orange-100 text-orange-700 border-orange-300" :
                  "bg-destructive/15 text-destructive border-destructive/30"
                )}>
                  {audit.zone} Zone
                </Badge>
              </div>
              <Progress value={Math.round((audit.total_score / audit.max_score) * 100)} className="h-2" />
            </div>
          ) : (
            <EmptyHint text="Take the lifestyle audit to see your health-zone score." />
          )}
        </PhaseCard>

        {/* Phase 3 — Descriptive Test */}
        <PhaseCard
          delay={0.2}
          number={3}
          icon={<PenTool className="w-5 h-5 text-primary" />}
          title="Descriptive Test"
          href="/descriptive-test"
          cta={descriptiveDone ? "Review Test" : "Begin Test"}
        >
          {descriptiveDone ? (
            <div className="flex items-center gap-2">
              <Badge className="text-xs bg-accent/20 text-accent border-accent/30">COMPLETED</Badge>
              <span className="font-body text-xs text-dark/50">Your responses have been saved.</span>
            </div>
          ) : (
            <EmptyHint text="Share your eating habits in your own words to complete this assessment." />
          )}
        </PhaseCard>
      </div>
    </AppShell>
  );
}

function DetailRow({ icon, label, value }: { icon: React.ReactNode; label: string; value?: string | number | null }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-xl bg-muted flex items-center justify-center text-dark/50 shrink-0">{icon}</div>
      <div className="min-w-0">
        <p className="font-body text-xs text-dark/40">{label}</p>
        <p className="font-body text-sm font-medium text-dark truncate">{value || "—"}</p>
      </div>
    </div>
  );
}

function PhaseCard({
  number,
  icon,
  title,
  href,
  cta,
  delay,
  children,
}: {
  number: number;
  icon: React.ReactNode;
  title: string;
  href: string;
  cta: string;
  delay: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0">{icon}</div>
            <div>
              <p className="font-body text-[11px] font-semibold uppercase tracking-widest text-primary/70">Phase {number}</p>
              <h3 className="font-heading text-base font-bold text-dark">{title}</h3>
            </div>
            <Link href={href} className="ml-auto">
              <Button size="sm" variant="ghost" className="text-primary hover:text-primary hover:bg-primary/10">
                {cta} <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );
}


function EmptyHint({ text }: { text: string }) {
  return <p className="font-body text-sm text-dark/50">{text}</p>;
}
