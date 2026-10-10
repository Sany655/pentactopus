import { deviceRoute, webRoute } from "@/lib/api";
import { getOwnedTask } from "@/lib/tasks";
import { HttpError, requireUuid, success } from "@/lib/http";
import { query } from "@/lib/db";

export const runtime = "nodejs";

type Context = { params: Promise<{ task_id: string }> };

export async function GET(request: Request, context: Context): Promise<Response> {
  const { task_id: taskId } = await context.params;
  if (request.headers.has("x-device-id")) {
    return deviceRoute(request, null, async (principal) => {
      requireUuid(taskId);
      const task = await getOwnedTask(principal.userId, taskId);
      const allowed = await query(
        `SELECT 1 FROM tasks
          WHERE user_id = $1 AND id = $2
            AND $3::uuid IN (origin_device_id, orchestrator_device_id, target_device_id)`,
        [principal.userId, taskId, principal.id],
      );
      if (!allowed.rowCount) {
        throw new HttpError(404, "not_found", "Task not found");
      }
      return success({ task });
    });
  }
  return webRoute(request, {}, async (principal) => {
    requireUuid(taskId);
    const task = await getOwnedTask(principal.id, taskId);
    return success({ task });
  });
}
