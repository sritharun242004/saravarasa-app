"use client";

import { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getAdminDashboard, getAdminClients, type AdminDashboard, type AdminClient } from "@/lib/api";
import { Loader2, Users, Trophy, RefreshCw, Lock, TrendingUp, IndianRupee, Search, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  QUALIFIED:     "bg-accent/20 text-accent border-accent/30",
  SECOND_CHANCE: "bg-primary/20 text-primary border-primary/30",
  LOCKED:        "bg-destructive/20 text-destructive border-destructive/30",
  ACTIVE:        "bg-muted text-dark/60 border-border",
};

type FilterKey = "all" | "audit_pending" | "audit_done" | "completed" | "in_progress" | "qualified" | "locked" | "has_report";

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all",           label: "All" },
  { key: "audit_pending", label: "Audit Pending" },
  { key: "audit_done",    label: "Audit Done" },
  { key: "in_progress",   label: "In Progress" },
  { key: "completed",     label: "Completed (7/7)" },
  { key: "qualified",     label: "Qualified" },
  { key: "locked",        label: "Locked" },
  { key: "has_report",    label: "Has Report" },
];

function applyFilter(clients: AdminClient[], filter: FilterKey): AdminClient[] {
  switch (filter) {
    case "audit_pending":  return clients.filter((c) => !c.audit_completed);
    case "audit_done":     return clients.filter((c) => c.audit_completed);
    case "in_progress":    return clients.filter((c) => (c.completed_days ?? 0) > 0 && (c.completed_days ?? 0) < 7);
    case "completed":      return clients.filter((c) => (c.completed_days ?? 0) >= 7);
    case "qualified":      return clients.filter((c) => c.status === "QUALIFIED");
    case "locked":         return clients.filter((c) => c.status === "LOCKED");
    case "has_report":     return clients.filter((c) => !!c.qualification_status);
    default:               return clients;
  }
}

function StatCard({ icon: Icon, label, value, color }: {
  icon: typeof Users; label: string; value: number | string; color: string;
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center mb-3", color)}>
          <Icon className="w-5 h-5" />
        </div>
        <p className="font-heading text-2xl font-bold text-dark">{value}</p>
        <p className="font-body text-xs text-dark/60 mt-0.5">{label}</p>
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [clients, setClients] = useState<AdminClient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterKey>("all");

  useEffect(() => {
    Promise.all([getAdminDashboard(), getAdminClients()])
      .then(([dash, clientData]) => {
        setDashboard(dash);
        setClients(clientData.clients || []);
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let list = applyFilter(clients, filter);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (c) => c.name?.toLowerCase().includes(q) || c.email?.toLowerCase().includes(q)
      );
    }
    return list;
  }, [clients, filter, search]);

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
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="font-heading text-3xl font-bold text-dark">Admin Dashboard</h1>
          <p className="font-body text-dark/60 mt-1">Sarvarasa platform overview</p>
        </motion.div>

        {/* Metrics Grid */}
        {dashboard && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
          >
            <StatCard icon={Users}       label="Total Users"      value={dashboard.total}          color="bg-muted" />
            <StatCard icon={TrendingUp}  label="Audit Completed"  value={dashboard.audit_completed} color="bg-primary/10 text-primary" />
            <StatCard icon={Trophy}      label="Qualified"         value={dashboard.qualified}       color="bg-accent/10 text-accent" />
            <StatCard icon={RefreshCw}   label="Second Chance"    value={dashboard.second_chance}   color="bg-primary/10 text-primary" />
            <StatCard icon={Lock}        label="Locked"            value={dashboard.locked}          color="bg-destructive/10 text-destructive" />
            <StatCard icon={RefreshCw}   label="Reactivated"      value={dashboard.reactivated}     color="bg-muted text-dark" />
            <StatCard icon={IndianRupee} label="Revenue"           value={`₹${dashboard.revenue_inr}`} color="bg-accent/10 text-accent" />
          </motion.div>
        )}

        {/* Clients Table */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="pb-3">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <CardTitle className="shrink-0">All Users ({clients.length})</CardTitle>
                {/* Search */}
                <div className="relative flex-1 max-w-xs">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark/30" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search name or email…"
                    className="w-full pl-9 pr-4 py-2 rounded-xl border border-border bg-card font-body text-sm text-dark placeholder:text-dark/40 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  />
                </div>
              </div>

              {/* Filter Tabs */}
              <div className="flex flex-wrap gap-1.5 mt-2">
                {FILTERS.map((f) => {
                  const count = applyFilter(clients, f.key).length;
                  return (
                    <button
                      key={f.key}
                      onClick={() => setFilter(f.key)}
                      className={cn(
                        "px-3 py-1 rounded-full text-xs font-body font-medium transition-colors border",
                        filter === f.key
                          ? "bg-primary text-white border-primary"
                          : "bg-card text-dark/60 border-border hover:border-primary/40 hover:text-dark"
                      )}
                    >
                      {f.label}
                      <span className={cn(
                        "ml-1.5 font-semibold",
                        filter === f.key ? "text-white/80" : "text-dark/40"
                      )}>
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </CardHeader>

            <CardContent className="pt-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm font-body">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Name</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Audit</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Days</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Compliance</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Status</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">Report</th>
                      <th className="text-left py-2 px-3 text-dark/50 font-medium text-xs">View</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((client) => (
                      <tr key={client.client_id} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                        <td className="py-3 px-3">
                          <p className="font-medium text-dark">{client.name}</p>
                          <p className="text-xs text-dark/40">{client.email}</p>
                        </td>
                        <td className="py-3 px-3">
                          {client.audit_completed ? (
                            <span className="text-accent text-xs font-medium">✓ Done</span>
                          ) : (
                            <span className="text-dark/30 text-xs">Pending</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-dark/70">
                          {client.completed_days ?? 0}
                          <span className="text-dark/30"> / 7</span>
                        </td>
                        <td className="py-3 px-3 font-semibold text-dark">
                          {client.compliance_pct ?? 0}%
                        </td>
                        <td className="py-3 px-3">
                          <Badge className={cn("text-xs", STATUS_COLORS[client.status] || STATUS_COLORS.ACTIVE)}>
                            {client.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-3">
                          {client.qualification_status ? (
                            <Link
                              href={`/admin/client/${client.client_id}#report`}
                              className="inline-flex items-center gap-1 text-accent text-xs hover:underline font-medium"
                            >
                              <FileText className="w-3 h-3" />
                              {client.qualification_status}
                            </Link>
                          ) : (
                            <span className="text-dark/25 text-xs">—</span>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          <Link
                            href={`/admin/client/${client.client_id}`}
                            className="text-primary text-xs hover:underline"
                          >
                            View →
                          </Link>
                        </td>
                      </tr>
                    ))}
                    {filtered.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-dark/40 text-sm">
                          {search ? `No users matching "${search}"` : "No users in this filter."}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AppShell>
  );
}
