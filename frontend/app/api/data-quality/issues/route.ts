import { NextRequest } from "next/server";
import { proxyToBackend } from "@/lib/backend";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const forwarded = new URLSearchParams();

  for (const key of ["type", "patient_id", "variable", "search", "page", "page_size"]) {
    const value = params.get(key);
    if (value) forwarded.set(key, value);
  }

  return proxyToBackend(`/data-quality/issues?${forwarded.toString()}`, {
    genericErrorMessage: "No fue posible cargar las incidencias de calidad de datos.",
  });
}
