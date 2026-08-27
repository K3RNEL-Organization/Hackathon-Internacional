import { proxyToBackend } from "@/lib/backend";

export async function GET(request: Request, { params }: { params: { signalId: string } }) {
  return proxyToBackend(`/signals/${encodeURIComponent(params.signalId)}`, {
    genericErrorMessage: "No fue posible cargar la información de la señal.",
  });
}
