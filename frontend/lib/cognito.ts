// Builds the AWS Cognito Hosted-UI authorize URL for Google federated sign-in.
// All values are public (they appear in the browser redirect) and come from
// NEXT_PUBLIC_ env vars — no secrets live on the client.

const COGNITO_DOMAIN = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || "";
const APP_CLIENT_ID = process.env.NEXT_PUBLIC_COGNITO_APP_CLIENT_ID || "";
const OAUTH_STATE_KEY = "sarvarasa_oauth_state";

export function getOAuthRedirectUri(): string {
  // Prefer an explicit env value; fall back to the current origin at runtime.
  if (process.env.NEXT_PUBLIC_OAUTH_REDIRECT_URI) {
    return process.env.NEXT_PUBLIC_OAUTH_REDIRECT_URI;
  }
  if (typeof window !== "undefined") {
    return `${window.location.origin}/auth/callback`;
  }
  return "";
}

export function isCognitoConfigured(): boolean {
  return Boolean(COGNITO_DOMAIN && APP_CLIENT_ID);
}

// Generates a fresh anti-CSRF `state` value, stashes it in sessionStorage so
// the callback page can verify the redirect it receives was one *this*
// browser initiated (not an attacker completing their own OAuth code
// exchange and binding the victim's session to the attacker's identity —
// "login CSRF"), and returns it for inclusion in the authorize URL.
function generateAndStoreState(): string {
  const state =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2) + Date.now().toString(36);
  if (typeof window !== "undefined") {
    sessionStorage.setItem(OAUTH_STATE_KEY, state);
  }
  return state;
}

export function consumeOAuthState(): string | null {
  if (typeof window === "undefined") return null;
  const state = sessionStorage.getItem(OAUTH_STATE_KEY);
  sessionStorage.removeItem(OAUTH_STATE_KEY);
  return state;
}

export function getGoogleLoginUrl(): string {
  const params = new URLSearchParams({
    client_id: APP_CLIENT_ID,
    response_type: "code",
    scope: "openid email profile",
    redirect_uri: getOAuthRedirectUri(),
    identity_provider: "Google",
    state: generateAndStoreState(),
  });
  return `${COGNITO_DOMAIN.replace(/\/$/, "")}/oauth2/authorize?${params.toString()}`;
}
