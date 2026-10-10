import { deviceRoute } from "@/lib/api";
import { createArtifact } from "@/lib/storage";
import { success } from "@/lib/http";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return deviceRoute(request, "artifactCreate", async (principal, body) => {
    return success(await createArtifact(principal, body as {
      task_id: string;
      intended_device_id: string;
      ciphertext_b64: string;
      media_type: string;
      expires_at: string;
    }), 201);
  });
}
