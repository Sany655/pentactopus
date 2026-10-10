import { getSession } from "@/lib/auth";
import { handle, HttpError, success } from "@/lib/http";

export const runtime = "nodejs";

export async function GET(request: Request): Promise<Response> {
  return handle(async () => {
    const session = await getSession(request);
    if (!session) throw new HttpError(401, "authentication_required", "Sign-in is required");
    return success({ user: session });
  });
}
