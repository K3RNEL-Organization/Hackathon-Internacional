import { proxyToBackend } from "@/lib/backend";

export async function GET() {
  return proxyToBackend("/auth/me", {
    genericErrorMessage: "No fue posible obtener la sesión.",
  });
}
