import { proxyToBackend } from "@/lib/backend";

export async function GET() {
  return proxyToBackend("/dashboard/summary", {
    genericErrorMessage: "No fue posible cargar la información del Dashboard.",
  });
}
