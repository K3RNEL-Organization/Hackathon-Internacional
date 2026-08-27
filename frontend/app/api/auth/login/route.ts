import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE } from "@/lib/session";

const API_URL = process.env.RISA_API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);

  if (!body || typeof body.email !== "string" || typeof body.password !== "string") {
    return NextResponse.json({ message: "Solicitud inválida." }, { status: 400 });
  }

  let backendResponse: Response;
  try {
    backendResponse = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: body.email, password: body.password }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { message: "No fue posible iniciar sesión. Intente nuevamente." },
      { status: 502 }
    );
  }

  if (backendResponse.status === 401) {
    return NextResponse.json({ message: "Credenciales incorrectas." }, { status: 401 });
  }

  if (!backendResponse.ok) {
    return NextResponse.json(
      { message: "No fue posible iniciar sesión. Intente nuevamente." },
      { status: 502 }
    );
  }

  const data = await backendResponse.json();

  const response = NextResponse.json({ role: data.role, name: data.name, email: data.email });
  response.cookies.set(SESSION_COOKIE, data.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  return response;
}
