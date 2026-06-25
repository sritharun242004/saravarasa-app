// Builds the AWS Cognito Hosted-UI authorize URL for Google federated sign-in.
// All values are public (they appear in the browser redirect) and come from
// NEXT_PUBLIC_ env vars — no secrets live on the client.

const COGNITO_DOMAIN = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || "";
const APP_CLIENT_ID = process.env.NEXT_PUBLIC_COGNITO_APP_CLIENT_ID || "";

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

export function getGoogleLoginUrl(): string {
  const params = new URLSearchParams({
    client_id: APP_CLIENT_ID,
    response_type: "code",
    scope: "openid email profile",
    redirect_uri: getOAuthRedirectUri(),
    identity_provider: "Google",
  });
  return `${COGNITO_DOMAIN.replace(/\/$/, "")}/oauth2/authorize?${params.toString()}`;
}
