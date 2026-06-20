"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/lib/use-toast";
import { createPaymentOrder, verifyPayment } from "@/lib/api";
import { Loader2, CheckCircle2, RefreshCw } from "lucide-react";

const CLIENT_ID_KEY = "sarvarasa_client_id";

declare global {
  interface Window {
    Razorpay: new (opts: Record<string, unknown>) => { open(): void };
  }
}

export default function ReactivatePage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const clientId = typeof window !== "undefined" ? localStorage.getItem(CLIENT_ID_KEY) || "" : "";

  const handlePay = async () => {
    if (!clientId) {
      toast({ title: "Not registered", description: "Please register first.", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      const order = await createPaymentOrder(clientId);

      if (!window.Razorpay) {
        // Load Razorpay script dynamically
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://checkout.razorpay.com/v1/checkout.js";
          script.onload = () => resolve();
          script.onerror = reject;
          document.body.appendChild(script);
        });
      }

      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "Sarvarasa",
        description: "Challenge Reactivation",
        order_id: order.order_id,
        handler: async (response: Record<string, string>) => {
          try {
            await verifyPayment({
              client_id: clientId,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            setSuccess(true);
            toast({ title: "Payment successful!", description: "Your challenge has been reactivated." });
            setTimeout(() => router.push("/challenge"), 2000);
          } catch {
            toast({ title: "Verification failed", description: "Please contact support.", variant: "destructive" });
          }
        },
        theme: { color: "#1B6040" },
      });
      rzp.open();
    } catch {
      toast({ title: "Error", description: "Could not initiate payment. Please try again.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh] px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center"
          >
            <CheckCircle2 className="w-16 h-16 text-accent mx-auto mb-4" />
            <h2 className="font-heading text-2xl font-bold text-dark mb-2">Reactivated!</h2>
            <p className="font-body text-dark/60">Redirecting to your challenge…</p>
          </motion.div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="max-w-lg mx-auto px-4 py-16">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <RefreshCw className="w-8 h-8 text-primary" />
            </div>
            <h1 className="font-heading text-3xl font-bold text-dark mb-2">Reactivate Challenge</h1>
            <p className="font-body text-dark/60">
              Your challenge is locked. Pay ₹299 to unlock a new challenge cycle.
            </p>
          </div>

          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-border">
                <span className="font-body text-sm text-dark">7-Day Wholesome Eating Challenge</span>
                <span className="font-heading text-xl font-bold text-primary">₹299</span>
              </div>

              <div className="space-y-2 text-sm font-body text-dark/60">
                <p className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-accent" />
                  Full 7-day challenge access
                </p>
                <p className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-accent" />
                  Food pattern analysis
                </p>
                <p className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-accent" />
                  Personalized food awareness report
                </p>
                <p className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-accent" />
                  Program qualification
                </p>
              </div>

              <Button onClick={handlePay} disabled={loading} size="lg" className="w-full">
                {loading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Processing…</>
                ) : (
                  "Pay ₹299 & Reactivate"
                )}
              </Button>

              <p className="text-center font-body text-xs text-dark/40">
                Secured by Razorpay · UPI, Cards, Net Banking accepted
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AppShell>
  );
}
