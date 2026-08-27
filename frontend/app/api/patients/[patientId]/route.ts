import { proxyToBackend } from "@/lib/backend";

export async function GET(request: Request, { params }: { params: { patientId: string } }) {
  return proxyToBackend(`/patients/${encodeURIComponent(params.patientId)}`, {
    genericErrorMessage: "No fue posible cargar la información del paciente.",
  });
}
