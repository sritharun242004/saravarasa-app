"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Calendar, BarChart2, ClipboardList } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const navItems = [
  { href: "/", icon: Home, label: "Home" },
  { href: "/audit", icon: ClipboardList, label: "Audit" },
  { href: "/challenge", icon: Calendar, label: "Challenge" },
  { href: "/dashboard", icon: BarChart2, label: "Dashboard" },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden glass border-t border-border/50">
      <div className="flex items-center justify-around px-2 py-2 pb-safe">
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className="flex flex-col items-center gap-1 py-2 px-4 rounded-xl cursor-pointer relative"
            >
              {active && (
                <motion.div
                  layoutId="bottom-nav-indicator"
                  className="absolute inset-0 bg-primary/10 rounded-xl"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                />
              )}
              <Icon
                className={cn(
                  "w-5 h-5 transition-colors duration-200",
                  active ? "text-primary" : "text-dark/40"
                )}
              />
              <span
                className={cn(
                  "text-[10px] font-medium font-body transition-colors duration-200",
                  active ? "text-primary" : "text-dark/40"
                )}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
