import { deviceRoute } from "@/lib/api";
import { requireUuid, success } from "@/lib/http";
import { readInbox } from "@/lib/storage";

export const runtime = "nodejs";

type Context = { params: Promise<{ inbox_id: string }> };

export async function GET(request: Request, context: Context): Promise<Response> {
  return deviceRoute(request, null, async (principal) => {
    const { inbox_id: inboxId } = await context.params;
    requireUuid(inboxId);
    return success(await readInbox(principal, inboxId));
  });
}
