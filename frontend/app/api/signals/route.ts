import { NextRequest } from "next/server";
import { proxyToBackend } from "@/lib/backend";

export async function GET(request: NextRequest) {
  const priority = request.nextUrl.searchParams.get("priority") ?? "ALL";
  return proxyToBackend(`/signals?priority=${encodeURIComponent(priority)}`, {
    genericErrorMessage: "No fue posible cargar las señales.",
  });
}
