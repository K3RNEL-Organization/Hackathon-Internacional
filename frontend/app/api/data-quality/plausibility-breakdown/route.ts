import { proxyToBackend } from "@/lib/backend";

export async function GET() {
  return proxyToBackend("/data-quality/plausibility-breakdown", {
    genericErrorMessage: "No fue posible cargar la distribución de valores atípicos.",
  });
}
