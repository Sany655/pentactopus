import { deviceRoute } from "@/lib/api";
import { requireUuid, success } from "@/lib/http";
import { acknowledgeInbox } from "@/lib/storage";

export const runtime = "nodejs";

type Context = { params: Promise<{ inbox_id: string }> };

export async function POST(request: Request, context: Context): Promise<Response> {
  return deviceRoute(request, "emptyObject", async (principal) => {
    const { inbox_id: inboxId } = await context.params;
    requireUuid(inboxId);
    await acknowledgeInbox(principal, inboxId);
    return success({ acknowledged: true });
  });
}
