"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function LandingCTA() {
  return (
    <section className="py-28 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden bg-primary text-primary-foreground rounded-[2.5rem] rounded-tr-[5rem] px-8 sm:px-16 py-16 text-center shadow-float"
        >
          {/* Inner organic blobs */}
          <div className="absolute -top-16 -right-10 w-72 h-72 bg-accent/30 blur-3xl blob-2 pointer-events-none" />
          <div className="absolute -bottom-20 -left-12 w-72 h-72 bg-secondary/25 blur-3xl blob-3 pointer-events-none" />

          <div className="relative z-10">
            <h2 className="font-heading text-4xl sm:text-5xl font-bold mb-4 text-balance">
              Ready to Begin?
            </h2>
            <p className="font-body text-primary-foreground/85 text-lg mb-8 max-w-xl mx-auto text-balance">
              Create your account to start the food challenge, lifestyle audit and descriptive test,
              all in one place.
            </p>
            <Link href="/signup">
              <Button size="lg" variant="secondary">
                Sign Up to Get Started
                <ArrowRight className="w-5 h-5 ml-1" />
              </Button>
            </Link>
            <p className="font-body text-primary-foreground/70 text-sm mt-6">
              Already have an account?{" "}
              <Link href="/login" className="text-primary-foreground font-bold hover:underline underline-offset-4">
                Log in here
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
