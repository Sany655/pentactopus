import { query } from "./db";
import { HttpError } from "./http";
import { sha256 } from "./security";

export const SESSION_COOKIE = "__Host-penta_session";
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

export type WebPrincipal = { id: string; email: string };

export function readSessionToken(request: Request): string | undefined {
  const cookieHeader = request.headers.get("cookie") ?? "";
  for (const field of cookieHeader.split(";")) {
    const [key, ...value] = field.trim().split("=");
    if (key === SESSION_COOKIE) return value.join("=");
  }
  return undefined;
}

export async function getSession(request: Request): Promise<WebPrincipal | null> {
  const token = readSessionToken(request);
  if (!token || !/^[A-Za-z0-9_-]{43}$/.test(token)) return null;
  const result = await query<{ id: string; email: string }>(
    `SELECT u.id, u.email
       FROM web_sessions s
       JOIN users u ON u.id = s.user_id
      WHERE s.token_hash = $1
        AND s.revoked_at IS NULL
        AND s.expires_at > now()
        AND u.disabled_at IS NULL`,
    [sha256(token)],
  );
  return result.rows[0] ?? null;
}

export async function requireSession(request: Request): Promise<WebPrincipal> {
  const session = await getSession(request);
  if (!session) throw new HttpError(401, "authentication_required", "Sign-in is required");
  return session;
}

export function assertSameOrigin(request: Request): void {
  const configured = process.env.APP_ORIGIN;
  if (!configured) throw new Error("APP_ORIGIN is required");
  const origin = request.headers.get("origin");
  if (!origin || origin !== new URL(configured).origin) {
    throw new HttpError(403, "origin_rejected", "Request origin is not allowed");
  }
}

export function sessionCookie(token: string): string {
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${SESSION_MAX_AGE_SECONDS}`;
}

export function clearSessionCookie(): string {
  return `${SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

export { SESSION_MAX_AGE_SECONDS };
