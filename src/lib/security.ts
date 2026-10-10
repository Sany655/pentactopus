import {
  createHash,
  createHmac,
  createPublicKey,
  randomBytes,
  timingSafeEqual,
  verify,
} from "node:crypto";
import { query } from "./db";
import { HttpError } from "./http";

const ED25519_SPKI_PREFIX = Buffer.from("302a300506032b6570032100", "hex");
const SIGNATURE_WINDOW_SECONDS = 300;

export function sha256(value: string | Uint8Array): Buffer {
  return createHash("sha256").update(value).digest();
}

export function randomToken(bytes = 32): string {
  return randomBytes(bytes).toString("base64url");
}

export function canonicalDeviceMessage(
  method: string,
  pathAndQuery: string,
  timestamp: string,
  nonce: string,
  body: Uint8Array,
): string {
  return [
    method.toUpperCase(),
    pathAndQuery,
    timestamp,
    nonce,
    createHash("sha256").update(body).digest("hex"),
  ].join("\n");
}

export function verifyDeviceSignature(
  rawPublicKey: Uint8Array,
  message: string,
  signature: Uint8Array,
): boolean {
  if (rawPublicKey.byteLength !== 32 || signature.byteLength !== 64) return false;
  try {
    const key = createPublicKey({
      key: Buffer.concat([ED25519_SPKI_PREFIX, Buffer.from(rawPublicKey)]),
      format: "der",
      type: "spki",
    });
    return verify(null, Buffer.from(message, "utf8"), key, signature);
  } catch {
    return false;
  }
}

export type DevicePrincipal = { id: string; userId: string; name: string };

export async function authenticateDevice(
  request: Request,
  rawBody: Uint8Array,
): Promise<DevicePrincipal> {
  const deviceId = request.headers.get("x-device-id") ?? "";
  const timestamp = request.headers.get("x-device-timestamp") ?? "";
  const nonce = request.headers.get("x-device-nonce") ?? "";
  const encodedSignature = request.headers.get("x-device-signature") ?? "";
  const timestampSeconds = Number(timestamp);
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(deviceId)
    || !/^\d{10}$/.test(timestamp)
    || Math.abs(Date.now() / 1000 - timestampSeconds) > SIGNATURE_WINDOW_SECONDS
    || !/^[A-Za-z0-9_-]{16,128}$/.test(nonce)
    || !/^[A-Za-z0-9_-]{86}$/.test(encodedSignature)
  ) {
    throw new HttpError(401, "invalid_device_signature", "Device authentication failed");
  }
  const result = await query<{ id: string; user_id: string; name: string; public_key: Buffer }>(
    `SELECT d.id, d.user_id, d.name, d.public_key
       FROM devices d JOIN users u ON u.id = d.user_id
      WHERE d.id = $1 AND d.revoked_at IS NULL AND u.disabled_at IS NULL`,
    [deviceId],
  );
  const device = result.rows[0];
  if (!device) throw new HttpError(401, "invalid_device_signature", "Device authentication failed");

  const pathAndQuery = new URL(request.url).pathname + new URL(request.url).search;
  const message = canonicalDeviceMessage(request.method, pathAndQuery, timestamp, nonce, rawBody);
  let signature: Buffer;
  try {
    signature = Buffer.from(encodedSignature, "base64url");
  } catch {
    throw new HttpError(401, "invalid_device_signature", "Device authentication failed");
  }
  if (signature.toString("base64url") !== encodedSignature) {
    throw new HttpError(401, "invalid_device_signature", "Device authentication failed");
  }
  if (!verifyDeviceSignature(device.public_key, message, signature)) {
    throw new HttpError(401, "invalid_device_signature", "Device authentication failed");
  }

  const replay = await query(
    `INSERT INTO device_nonces (device_id, nonce, request_timestamp, expires_at)
     VALUES ($1, $2, to_timestamp($3), now() + interval '10 minutes')
     ON CONFLICT (device_id, nonce) DO NOTHING
     RETURNING nonce`,
    [device.id, nonce, timestampSeconds],
  );
  if (!replay.rowCount) throw new HttpError(401, "replayed_request", "Device authentication failed");
  if (Math.random() < 0.01) {
    await query("DELETE FROM device_nonces WHERE expires_at < now()");
  }

  return { id: device.id, userId: device.user_id, name: device.name };
}

export async function requestIp(request: Request): Promise<string> {
  return request.headers.get("x-real-ip")
    ?? request.headers.get("x-forwarded-for")?.split(",").at(-1)?.trim()
    ?? "unknown";
}

export async function enforceRateLimit(
  request: Request,
  routeKey: string,
  limit: number,
  windowSeconds: number,
  identifier?: string,
): Promise<void> {
  const secret = process.env.RATE_LIMIT_HMAC_KEY;
  if (!secret || Buffer.byteLength(secret) < 32) {
    throw new Error("RATE_LIMIT_HMAC_KEY must contain at least 32 bytes");
  }
  const now = new Date();
  const windowMs = windowSeconds * 1000;
  const startMs = Math.floor(now.getTime() / windowMs) * windowMs;
  const identity = identifier ?? await requestIp(request);
  const bucket = createHmac("sha256", secret)
    .update(`${routeKey}\n${identity}\n${startMs}`)
    .digest();
  const result = await query<{ hit_count: number }>(
    `INSERT INTO rate_limit_buckets (bucket_hash, window_start, hit_count, expires_at)
     VALUES ($1, to_timestamp($2 / 1000.0), 1, to_timestamp($2 / 1000.0) + ($3 * interval '1 second'))
     ON CONFLICT (bucket_hash) DO UPDATE
       SET hit_count = rate_limit_buckets.hit_count + 1
       WHERE rate_limit_buckets.expires_at > now()
     RETURNING hit_count`,
    [bucket, startMs, windowSeconds * 2],
  );
  if (!result.rowCount || result.rows[0].hit_count > limit) {
    throw new HttpError(429, "rate_limited", "Too many requests; please try again later");
  }
  if (startMs % (windowMs * 10) < 1000) {
    await query("DELETE FROM rate_limit_buckets WHERE expires_at < now()");
  }
}

export function safeEqualHex(left: string, right: string): boolean {
  if (!/^[a-f0-9]{64}$/i.test(left) || !/^[a-f0-9]{64}$/i.test(right)) return false;
  return timingSafeEqual(Buffer.from(left, "hex"), Buffer.from(right, "hex"));
}
