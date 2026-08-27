import { jwtVerify } from "jose";

export const SESSION_COOKIE = "risa_session";

const JWT_SECRET = process.env.RISA_JWT_SECRET ?? "risa-data-dev-secret-change-me";

export type SessionRole = "PROFESIONAL_SALUD" | "ADMINISTRADOR";

export interface SessionPayload {
  sub: string;
  role: SessionRole;
}

export async function verifySessionToken(token: string): Promise<SessionPayload | null> {
  try {
    const { payload } = await jwtVerify(token, new TextEncoder().encode(JWT_SECRET));
    if (typeof payload.sub !== "string" || typeof payload.role !== "string") {
      return null;
    }
    return { sub: payload.sub, role: payload.role as SessionRole };
  } catch {
    return null;
  }
}

export function roleHomePath(role: SessionRole): string {
  return role === "ADMINISTRADOR" ? "/admin" : "/dashboard";
}
