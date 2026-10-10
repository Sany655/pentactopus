import { validateApiPayload } from "./contracts";

export const API_SCHEMA_VERSION = "1.0.3";
const MAX_JSON_BODY_BYTES = 2 * 1024 * 1024;

export class HttpError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

export function success(data: unknown, status = 200): Response {
  return Response.json(
    { schema_version: API_SCHEMA_VERSION, data },
    { status, headers: { "Cache-Control": "no-store, max-age=0", Pragma: "no-cache" } },
  );
}

export function failure(error: unknown): Response {
  const known = error instanceof HttpError
    ? error
    : new HttpError(500, "internal_error", "An internal error occurred");
  if (known.status >= 500) console.error("API request failed", known.code, error);
  return Response.json(
    {
      schema_version: API_SCHEMA_VERSION,
      error: { code: known.code, message: known.message },
    },
    { status: known.status, headers: { "Cache-Control": "no-store, max-age=0", Pragma: "no-cache" } },
  );
}

export async function handle(
  operation: () => Promise<Response>,
): Promise<Response> {
  try {
    return await operation();
  } catch (error) {
    return failure(error);
  }
}

export async function readJson(
  request: Request,
  maxBytes = MAX_JSON_BODY_BYTES,
): Promise<{ value: unknown; raw: Uint8Array }> {
  const contentLength = Number(request.headers.get("content-length") ?? 0);
  if (contentLength > maxBytes) throw new HttpError(413, "body_too_large", "Request body is too large");
  if (!request.body) return { value: {}, raw: new Uint8Array() };

  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let length = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    length += value.byteLength;
    if (length > maxBytes) {
      await reader.cancel();
      throw new HttpError(413, "body_too_large", "Request body is too large");
    }
    chunks.push(value);
  }
  const raw = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    raw.set(chunk, offset);
    offset += chunk.byteLength;
  }
  try {
    return { value: JSON.parse(new TextDecoder().decode(raw)), raw };
  } catch {
    throw new HttpError(400, "invalid_json", "Request body must be valid JSON");
  }
}

export function requireContract(name: string, value: unknown): void {
  if (!validateApiPayload(name, value)) {
    throw new HttpError(400, "invalid_request", "Request does not match the API contract");
  }
}

export function requireUuid(value: string): string {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value)) {
    throw new HttpError(404, "not_found", "Resource not found");
  }
  return value;
}

export function noContent(): Response {
  return new Response(null, {
    status: 204,
    headers: { "Cache-Control": "no-store, max-age=0", Pragma: "no-cache" },
  });
}
