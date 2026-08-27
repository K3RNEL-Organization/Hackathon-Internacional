import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { SESSION_COOKIE } from "@/lib/session";

const API_URL = process.env.RISA_API_URL ?? "http://localhost:8000";

export async function proxyToBackend(
  path: string,
  options?: { genericErrorMessage?: string }
): Promise<NextResponse> {
  const genericErrorMessage =
    options?.genericErrorMessage ?? "No fue posible cargar la información solicitada.";
  const token = cookies().get(SESSION_COOKIE)?.value;

  if (!token) {
    return NextResponse.json({ message: "Sesión inválida." }, { status: 401 });
  }

  let backendResponse: Response;
  try {
    backendResponse = await fetch(`${API_URL}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ message: genericErrorMessage }, { status: 502 });
  }

  if (backendResponse.status === 401) {
    return NextResponse.json({ message: "Sesión inválida." }, { status: 401 });
  }

  if (backendResponse.status === 404) {
    const data = await backendResponse.json().catch(() => ({}));
    return NextResponse.json(
      { message: data.detail ?? "No encontrado." },
      { status: 404 }
    );
  }

  if (!backendResponse.ok) {
    return NextResponse.json({ message: genericErrorMessage }, { status: 502 });
  }

  const data = await backendResponse.json();
  return NextResponse.json(data);
}
