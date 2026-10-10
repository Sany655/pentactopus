import { assertSameOrigin, requireSession, type WebPrincipal } from "./auth";
import { authenticateDevice, type DevicePrincipal } from "./security";
import { handle, readJson, requireContract } from "./http";

export function deviceRoute<T>(
  request: Request,
  schema: string | null,
  operation: (principal: DevicePrincipal, body: T) => Promise<Response>,
): Promise<Response> {
  return handle(async () => {
    const parsed = await readJson(request);
    if (schema) requireContract(schema, parsed.value);
    const principal = await authenticateDevice(request, parsed.raw);
    return operation(principal, parsed.value as T);
  });
}

export function webRoute<T>(
  request: Request,
  options: { mutation?: boolean; schema?: string },
  operation: (principal: WebPrincipal, body: T) => Promise<Response>,
): Promise<Response> {
  return handle(async () => {
    if (options.mutation) assertSameOrigin(request);
    const principal = await requireSession(request);
    const parsed = options.mutation ? await readJson(request) : { value: {} };
    if (options.schema) requireContract(options.schema, parsed.value);
    return operation(principal, parsed.value as T);
  });
}
