import { deviceRoute } from "@/lib/api";
import { decideApproval } from "@/lib/tasks";
import { requireUuid, success } from "@/lib/http";

export const runtime = "nodejs";

type Context = { params: Promise<{ task_id: string }> };

export async function POST(request: Request, context: Context): Promise<Response> {
  const { task_id: taskId } = await context.params;
  return deviceRoute(request, "approvalDecision", async (principal, body) => {
    requireUuid(taskId);
    return success(await decideApproval(principal, taskId, body as {
      approval_id: string;
      action_hash: string;
      decision: "approve" | "reject";
    }));
  });
}
