import { deviceRoute } from "@/lib/api";
import { requireUuid, success } from "@/lib/http";
import { transitionTask, type TaskStatus } from "@/lib/tasks";
import { validateTaskEnvelope } from "@/lib/contracts";

export const runtime = "nodejs";

type Context = { params: Promise<{ task_id: string }> };

export async function POST(request: Request, context: Context): Promise<Response> {
  const { task_id: taskId } = await context.params;
  return deviceRoute(request, "taskTransition", async (principal, body) => {
    requireUuid(taskId);
    const result = await transitionTask(principal, taskId, body as {
      status: TaskStatus;
      outcome_code?: string;
      approval_id?: string;
      action_hash?: string;
      local_confirmation?: boolean;
    });
    if (!validateTaskEnvelope(result)) throw new Error("Updated task does not match the task envelope contract");
    return success({ task: result });
  });
}
