import { deviceRoute } from "@/lib/api";
import { claimTask } from "@/lib/tasks";
import { noContent, requireUuid, success } from "@/lib/http";
import { validateTaskEnvelope } from "@/lib/contracts";

export const runtime = "nodejs";

type Context = { params: Promise<{ task_id: string }> };

export async function POST(request: Request, context: Context): Promise<Response> {
  const { task_id: taskId } = await context.params;
  return deviceRoute(request, "emptyObject", async (principal) => {
    requireUuid(taskId);
    const task = await claimTask(principal, taskId);
    if (!task) return noContent();
    if (!validateTaskEnvelope(task)) throw new Error("Claimed task does not match the task envelope contract");
    return success({ task });
  });
}
