import { deviceRoute } from "@/lib/api";
import { createApproval } from "@/lib/tasks";
import { requireUuid, success } from "@/lib/http";

export const runtime = "nodejs";

type Context = { params: Promise<{ task_id: string }> };

export async function POST(request: Request, context: Context): Promise<Response> {
  const { task_id: taskId } = await context.params;
  return deviceRoute(request, "approvalRequest", async (principal, body) => {
    requireUuid(taskId);
    return success(await createApproval(principal, taskId, body as {
      action_hash: string;
      tier: 4 | 5;
      preview_inbox_ids: string[];
    }), 201);
  });
}
