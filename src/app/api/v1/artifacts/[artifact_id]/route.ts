import { deviceRoute } from "@/lib/api";
import { requireUuid, success } from "@/lib/http";
import { readArtifact } from "@/lib/storage";

export const runtime = "nodejs";

type Context = { params: Promise<{ artifact_id: string }> };

export async function GET(request: Request, context: Context): Promise<Response> {
  return deviceRoute(request, null, async (principal) => {
    const { artifact_id: artifactId } = await context.params;
    requireUuid(artifactId);
    return success(await readArtifact(principal, artifactId));
  });
}
