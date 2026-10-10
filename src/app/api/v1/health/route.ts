import { success } from "@/lib/http";

export const runtime = "nodejs";

export function GET(): Response {
  return success({ status: "ok" });
}
