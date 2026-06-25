"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, AlertCircle } from "lucide-react";
import { exchangeCognitoCode } from "@/lib/api";
import { getOAuthRedirectUri } from "@/lib/cognito";
import { Button } from "@/components/ui/button";

const CLIENT_ID_KEY = "sarvarasa_client_id";
const CLIENT_NAME_KEY = "sarvarasa_client_name";
const TOKEN_KEY = "sarvarasa_token";

function CallbackInner() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return; // guard against React 18 double-invoke
    ran.current = true;

    const code = params.get("code");
    const oauthError = params.get("error_description") || params.get("error");

    if (oauthError) {
      setError(oauthError);
      return;
    }
    if (!code) {
      setError("No authorization code returned from Google.");
      return;
    }

    exchangeCognitoCode(code, getOAuthRedirectUri())
      .then((res) => {
        localStorage.setItem(CLIENT_ID_KEY, res.client_id);
        localStorage.setItem(CLIENT_NAME_KEY, res.name);
        if (res.token) localStorage.setItem(TOKEN_KEY, res.token);
        // Send Google sign-ins through the follow-up page to capture phone, etc.
        router.replace("/complete-profile?next=/challenge");
      })
      .catch((err: unknown) => {
        const msg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          "Sign-in failed. Please try again.";
        setError(msg);
      });
  }, [params, router]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-gradient-to-br from-gray-50 to-white">
      {error ? (
        <div className="text-center max-w-sm">
          <div className="w-12 h-12 rounded-2xl bg-red-100 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-red-600" />
          </div>
          <h1 className="font-heading text-xl font-bold text-gray-900 mb-2">Sign-in failed</h1>
          <p className="font-body text-sm text-gray-600 mb-6">{error}</p>
          <Button onClick={() => router.replace("/signup")} className="bg-blue-600 hover:bg-blue-700 text-white">
            Back to Sign Up
          </Button>
        </div>
      ) : (
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="font-body text-gray-600">Signing you in…</p>
        </div>
      )}
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      }
    >
      <CallbackInner />
    </Suspense>
  );
}
