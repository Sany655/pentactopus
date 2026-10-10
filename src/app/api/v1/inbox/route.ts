import { deviceRoute } from "@/lib/api";
import { createInbox } from "@/lib/storage";
import { success } from "@/lib/http";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return deviceRoute(request, "inboxCreate", async (principal, body) => {
    const result = await createInbox(principal, body as {
      task_id: string;
      target_device_id: string;
      ciphertext_b64: string;
      expires_at: string;
    });
    return success(result, 201);
  });
}
