"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { User, Menu, X, LogOut, ShieldCheck } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const ADMIN_TOKEN_KEY = "sarvarasa_admin_token";
const ADMIN_EMAIL_KEY = "sarvarasa_admin_email";

const LINKS = [
  { href: "/challenge", label: "Food Challenge" },
  { href: "/audit", label: "Lifestyle Audit" },
  { href: "/descriptive-test", label: "Descriptive Test" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem(CLIENT_ID_KEY));
    setIsAdmin(!!localStorage.getItem(ADMIN_TOKEN_KEY));
  }, [pathname]);

  const adminLogout = () => {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    localStorage.removeItem(ADMIN_EMAIL_KEY);
    setIsAdmin(false);
    router.push("/admin/login");
  };

  // Close the mobile menu on route change.
  useEffect(() => setMenuOpen(false), [pathname]);

  return (
    <div className="fixed top-3 left-0 right-0 z-40 px-4">
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="max-w-6xl mx-auto glass rounded-full shadow-soft"
      >
        <div className="flex items-center justify-between gap-3 pl-3 pr-2.5 py-2">
          {/* Logo — pale wordmark on a green chip so it reads on the light nav */}
          <Link href="/" className="flex items-center cursor-pointer shrink-0">
            <span className="flex items-center rounded-full bg-primary pl-3 pr-4 py-2 shadow-soft">
              <Image
                src="/logo-in-light-colour.png"
                alt="Sarvarasa"
                width={122}
                height={32}
                className="h-6 w-auto object-contain"
                priority
              />
            </span>
          </Link>

          {/* Desktop links (logged in) */}
          {isLoggedIn && (
            <nav className="hidden md:flex items-center gap-1">
              {LINKS.map((l) => {
                const active = pathname.startsWith(l.href);
                return (
                  <Link
                    key={l.href}
                    href={l.href}
                    className={cn(
                      "px-4 py-2 rounded-full text-sm font-semibold font-body transition-colors",
                      active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:text-primary hover:bg-primary/5",
                    )}
                  >
                    {l.label}
                  </Link>
                );
              })}
            </nav>
          )}

          {/* Right cluster */}
          <div className="flex items-center gap-2 shrink-0">
            {isAdmin ? (
              <>
                <Link href="/admin" className="hidden sm:block">
                  <Button size="sm" variant="ghost" className="text-primary">
                    <ShieldCheck className="w-4 h-4 mr-1.5" /> Admin
                  </Button>
                </Link>
                <Button size="sm" variant="secondary" onClick={adminLogout}>
                  <LogOut className="w-4 h-4 mr-1.5" /> Logout
                </Button>
              </>
            ) : isLoggedIn ? (
              <Link href="/profile" className="hidden md:block">
                <Button size="sm" variant="ghost" className="text-primary">
                  <User className="w-4 h-4 mr-1.5" /> Profile
                </Button>
              </Link>
            ) : (
              <>
                <Link href="/login" className="hidden sm:block">
                  <Button size="sm" variant="ghost" className="text-primary">Log In</Button>
                </Link>
                <Link href="/signup">
                  <Button size="sm" variant="secondary">Sign Up</Button>
                </Link>
              </>
            )}

            {/* Mobile menu toggle */}
            <button
              type="button"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              onClick={() => setMenuOpen((o) => !o)}
              className="md:hidden w-10 h-10 rounded-full flex items-center justify-center text-primary hover:bg-primary/10 transition-colors"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </motion.header>

      {/* Mobile dropdown panel */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="md:hidden max-w-6xl mx-auto mt-2 glass rounded-[2rem] shadow-float p-3"
          >
            <nav className="flex flex-col gap-1">
              {(isLoggedIn ? LINKS : []).map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className={cn(
                    "px-4 py-3 rounded-2xl text-sm font-semibold font-body transition-colors",
                    pathname.startsWith(l.href) ? "bg-primary/10 text-primary" : "text-dark/70 hover:bg-primary/5 hover:text-primary",
                  )}
                >
                  {l.label}
                </Link>
              ))}
              <div className="h-px bg-border/60 my-1" />
              {isAdmin ? (
                <div className="flex gap-2 p-1">
                  <Link href="/admin" className="flex-1">
                    <Button variant="outline" className="w-full">
                      <ShieldCheck className="w-4 h-4 mr-1.5" /> Admin
                    </Button>
                  </Link>
                  <Button className="flex-1" onClick={adminLogout}>
                    <LogOut className="w-4 h-4 mr-1.5" /> Logout
                  </Button>
                </div>
              ) : isLoggedIn ? (
                <Link href="/profile" className="px-4 py-3 rounded-2xl text-sm font-semibold font-body text-dark/70 hover:bg-primary/5 hover:text-primary flex items-center gap-2">
                  <User className="w-4 h-4" /> Profile
                </Link>
              ) : (
                <div className="flex gap-2 p-1">
                  <Link href="/login" className="flex-1">
                    <Button variant="outline" className="w-full">Log In</Button>
                  </Link>
                  <Link href="/signup" className="flex-1">
                    <Button className="w-full">Sign Up</Button>
                  </Link>
                </div>
              )}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
