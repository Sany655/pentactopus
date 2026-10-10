import { deviceRoute } from "@/lib/api";
import { createTask } from "@/lib/tasks";
import { requireContract, success } from "@/lib/http";
import { validateTaskEnvelope } from "@/lib/contracts";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return deviceRoute(request, "taskCreate", async (principal, body) => {
    requireContract("taskCreate", body);
    const task = await createTask(principal, body as {
      target_device_id: string;
      parent_task_id?: string;
      capability: string;
      body: Record<string, unknown>;
      input_refs: string[];
      requires_confirmation: boolean;
      expires_at: string;
    });
    if (!validateTaskEnvelope(task)) throw new Error("Created task does not match the task envelope contract");
    return success({ task }, 201);
  });
}
