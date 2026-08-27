import { proxyToBackend } from "@/lib/backend";

export async function GET() {
  return proxyToBackend("/data-quality/summary", {
    genericErrorMessage: "No fue posible cargar el resumen de calidad de datos.",
  });
}
