"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getAdminClientDetail, type AdminClientDetail } from "@/lib/api";
import { Loader2, ArrowLeft, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MEAL_ORDER = ["BREAKFAST", "LUNCH", "DINNER", "SNACK"];

export default function AdminClientPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const [detail, setDetail] = useState<AdminClientDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminClientDetail(clientId)
      .then(setDetail)
      .finally(() => setLoading(false));
  }, [clientId]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (!detail) return null;

  const { client, audit, compliance, meal_timeline, report, payment_history } = detail;

  // Group timeline by cycle and day
  const byDay: Record<string, typeof meal_timeline> = {};
  for (const entry of meal_timeline || []) {
    const key = `${entry.challenge_cycle}_${entry.day}`;
    byDay[key] = byDay[key] || [];
    byDay[key].push(entry);
  }

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Link href="/admin">
            <Button variant="ghost" size="sm" className="p-2">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="font-heading text-2xl font-bold text-dark">{client.name}</h1>
            <p className="font-body text-sm text-dark/60">{client.email} · {client.phone}</p>
          </div>
          <Badge className={cn(
            "ml-auto",
            client.status === "QUALIFIED" ? "bg-accent/20 text-accent" :
            client.status === "LOCKED" ? "bg-destructive/20 text-destructive" : "bg-muted text-dark/60"
          )}>
            {client.status}
          </Badge>
        </div>

        {/* Profile */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Profile</CardTitle></CardHeader>
          <CardContent className="grid grid-cols-2 gap-2 text-sm font-body">
            {[
              ["Age", client.age],
              ["Gender", client.gender],
              ["Cycle", client.challenge_cycle],
              ["Audit", client.audit_completed ? "✓ Completed" : "Pending"],
            ].map(([l, v]) => (
              <div key={String(l)}>
                <p className="text-dark/50 text-xs">{l}</p>
                <p className="text-dark font-medium">{String(v ?? "—")}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Audit */}
        {audit && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Lifestyle Audit</CardTitle></CardHeader>
            <CardContent className="grid grid-cols-2 gap-2 text-sm font-body">
              {[
                ["Sleep", audit.sleep_hours],
                ["Activity", audit.activity_level],
                ["Meals/Day", audit.meals_per_day],
                ["Outside Food", audit.outside_food_frequency],
                ["Stress", audit.stress_level],
              ].map(([l, v]) => (
                <div key={String(l)}>
                  <p className="text-dark/50 text-xs">{l}</p>
                  <p className="text-dark font-medium">{String(v ?? "—")}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Compliance */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Compliance</CardTitle></CardHeader>
          <CardContent className="text-sm font-body space-y-1">
            <p>Completed Days: <strong>{compliance?.completed_days ?? 0} / 7</strong></p>
            <p>Compliance: <strong>{compliance?.compliance_pct ?? 0}%</strong></p>
            <p>Status: <strong>{compliance?.status}</strong></p>
          </CardContent>
        </Card>

        {/* Image Timeline */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Meal Timeline</CardTitle></CardHeader>
          <CardContent>
            {meal_timeline?.length === 0 ? (
              <p className="font-body text-sm text-dark/40">No meals submitted yet.</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(byDay).sort().map(([key, entries]) => {
                  const [cycle, day] = key.split("_");
                  return (
                    <div key={key}>
                      <p className="font-body text-xs text-dark/50 mb-2 uppercase tracking-wide">
                        Cycle {cycle} · Day {day}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {entries
                          .sort((a, b) => MEAL_ORDER.indexOf(a.meal_type) - MEAL_ORDER.indexOf(b.meal_type))
                          .map((entry) => (
                          <div key={entry.meal_type} className="border border-border rounded-xl overflow-hidden">
                            {entry.image_url && (
                              <div className="relative h-28">
                                <Image
                                  src={`${API_URL}${entry.image_url}`}
                                  alt={entry.meal_type}
                                  fill
                                  className="object-cover"
                                />
                              </div>
                            )}
                            <div className="p-3">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-body text-xs font-semibold text-dark/60 uppercase">{entry.meal_type}</span>
                                {entry.image_url ? (
                                  <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
                                ) : (
                                  <XCircle className="w-3.5 h-3.5 text-destructive/50" />
                                )}
                              </div>
                              <p className="font-body text-xs text-dark/70 leading-relaxed">{entry.meal_text}</p>
                              {entry.food_pattern_tags?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {entry.food_pattern_tags.map((tag: string) => (
                                    <span key={tag} className="text-[10px] bg-muted px-1.5 py-0.5 rounded-full text-dark/50">
                                      {tag.replace(/_/g, " ")}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Report */}
        {report && (
          <Card id="report">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Challenge Report</CardTitle>
                <span className={cn(
                  "text-xs font-semibold px-2.5 py-1 rounded-full",
                  report.qualification_status === "QUALIFIED"
                    ? "bg-accent/20 text-accent"
                    : report.qualification_status === "SECOND_CHANCE"
                    ? "bg-primary/20 text-primary"
                    : "bg-destructive/20 text-destructive"
                )}>
                  {report.qualification_status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="text-sm font-body space-y-4">
              {/* Summary row */}
              <div className="grid grid-cols-3 gap-3">
                {[
                  ["Compliance", `${report.compliance_score}%`],
                  ["Days Done", `${report.completed_days} / 7`],
                  ["Band", report.band_label || report.eligibility_band || "—"],
                ].map(([l, v]) => (
                  <div key={l} className="bg-muted/40 rounded-xl p-3 text-center">
                    <p className="text-xs text-dark/50 mb-0.5">{l}</p>
                    <p className="font-semibold text-dark text-sm">{v}</p>
                  </div>
                ))}
              </div>

              {/* Food observations */}
              {report.food_observations?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-dark/50 uppercase tracking-wide mb-1.5">Food Observations</p>
                  <ul className="space-y-1">
                    {report.food_observations.map((obs, i) => (
                      <li key={i} className="flex gap-2 text-dark/80">
                        <span className="text-primary mt-0.5 shrink-0">•</span>{obs}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Strengths */}
              {report.strengths?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-accent uppercase tracking-wide mb-1.5">Strengths</p>
                  <ul className="space-y-1">
                    {report.strengths.map((s, i) => (
                      <li key={i} className="flex gap-2 text-dark/80">
                        <span className="text-accent mt-0.5 shrink-0">✓</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Improvement areas */}
              {report.improvement_areas?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-destructive/70 uppercase tracking-wide mb-1.5">Areas to Improve</p>
                  <ul className="space-y-1">
                    {report.improvement_areas.map((s, i) => (
                      <li key={i} className="flex gap-2 text-dark/80">
                        <span className="text-destructive/60 mt-0.5 shrink-0">→</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action plan */}
              {report.action_plan?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-1.5">Action Plan</p>
                  <ul className="space-y-1">
                    {report.action_plan.map((s, i) => (
                      <li key={i} className="flex gap-2 text-dark/80">
                        <span className="text-primary font-semibold shrink-0">{i + 1}.</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Wholesome plate tips */}
              {report.wholesome_plate_tips?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-dark/50 uppercase tracking-wide mb-1.5">Wholesome Plate Tips</p>
                  <ul className="space-y-1">
                    {report.wholesome_plate_tips.map((s, i) => (
                      <li key={i} className="flex gap-2 text-dark/80">
                        <span className="shrink-0">🌿</span>{s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Food pattern summary */}
              {Object.keys(report.food_pattern_summary || {}).length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-dark/50 uppercase tracking-wide mb-1.5">Food Pattern Tags</p>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(report.food_pattern_summary).map(([tag, count]) => (
                      <span key={tag} className="text-xs bg-muted px-2.5 py-1 rounded-full text-dark/60">
                        {tag.replace(/_/g, " ")} <span className="font-semibold text-dark">{count}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs text-dark/30 pt-1">
                Generated {new Date(report.generated_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
              </p>
            </CardContent>
          </Card>
        )}

        {/* No report yet */}
        {!report && (
          <Card className="border-dashed">
            <CardContent className="py-6 text-center text-dark/40 text-sm font-body">
              No report generated yet for this user.
            </CardContent>
          </Card>
        )}

        {/* Payments */}
        {payment_history?.length > 0 && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Payment History</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {payment_history.map((p) => (
                <div key={p.transaction_id} className="flex justify-between items-center py-2 border-b border-border/50 last:border-0 text-sm font-body">
                  <span className="text-dark/70">₹{p.amount_inr} · Cycle {p.cycle_unlocked}</span>
                  <Badge className={p.status === "PAID" ? "bg-accent/20 text-accent" : "bg-muted text-dark/60"}>
                    {p.status}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
