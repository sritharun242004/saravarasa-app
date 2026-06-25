"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { User, Zap, Brain, PenTool, Lock } from "lucide-react";
import { cn } from "@/lib/utils";

interface Tab {
  id: string;
  label: string;
  href: string;
  icon: React.ReactNode;
  locked?: boolean;
  lockReason?: string;
}

interface AppTabsProps {
  tabs?: Tab[];
  isLocked?: boolean;
  lockReasons?: { [key: string]: string };
}

export function AppTabs({ tabs, isLocked = false, lockReasons = {} }: AppTabsProps) {
  const pathname = usePathname();

  const defaultTabs: Tab[] = [
    {
      id: "profile",
      label: "Profile",
      href: "/app/profile",
      icon: <User className="w-5 h-5" />,
    },
    {
      id: "challenge",
      label: "7-Day Challenge",
      href: "/app/challenge",
      icon: <Zap className="w-5 h-5" />,
    },
    {
      id: "mcq",
      label: "Lifestyle Audit",
      href: "/app/lifestyle-audit",
      icon: <Brain className="w-5 h-5" />,
      locked: false,
      lockReason: "Complete 85%+ of the challenge",
    },
    {
      id: "descriptive",
      label: "Descriptive Test",
      href: "/app/descriptive-test",
      icon: <PenTool className="w-5 h-5" />,
      locked: true,
      lockReason: "Complete MCQ test first",
    },
  ];

  const displayTabs = tabs || defaultTabs;
  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <div className="fixed bottom-0 left-0 right-0 border-t border-border bg-background/95 backdrop-blur-sm md:static md:border-b md:border-t-0">
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex md:flex-row overflow-x-auto md:overflow-visible gap-1">
          {displayTabs.map((tab) => {
            const active = isActive(tab.href);
            const locked = tab.locked || isLocked;

            return (
              <div key={tab.id} className="flex-shrink-0 md:flex-shrink">
                {locked ? (
                  <div
                    className="relative group flex items-center gap-2 px-4 py-3 cursor-not-allowed opacity-50"
                    title={tab.lockReason || "Tab locked"}
                  >
                    <Lock className="w-4 h-4" />
                    <span className="text-sm font-medium hidden sm:inline">{tab.label}</span>

                    <div className="absolute bottom-full left-0 mb-2 bg-dark text-white text-xs px-2 py-1 rounded whitespace-nowrap hidden group-hover:block">
                      {tab.lockReason || "Tab locked"}
                    </div>
                  </div>
                ) : (
                  <Link href={tab.href}>
                    <motion.button
                      className={cn(
                        "relative flex items-center gap-2 px-4 py-3 font-medium transition-colors text-sm",
                        active
                          ? "text-primary"
                          : "text-dark/60 hover:text-dark/80"
                      )}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {tab.icon}
                      <span className="hidden sm:inline">{tab.label}</span>

                      {active && (
                        <motion.div
                          layoutId="active-tab"
                          className="absolute inset-x-0 bottom-0 h-1 bg-primary"
                          transition={{ type: "spring", stiffness: 500, damping: 30 }}
                        />
                      )}
                    </motion.button>
                  </Link>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Mobile safe area spacer */}
      <div className="h-0.5 md:hidden" />
    </div>
  );
}
