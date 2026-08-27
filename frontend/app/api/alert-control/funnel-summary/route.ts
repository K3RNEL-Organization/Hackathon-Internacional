import { proxyToBackend } from "@/lib/backend";

export async function GET() {
  return proxyToBackend("/alert-control/funnel-summary", {
    genericErrorMessage: "No fue posible cargar el resumen de control de alertas.",
  });
}
