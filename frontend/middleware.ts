import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE, roleHomePath, verifySessionToken } from "./lib/session";

const ROUTE_ROLES: Record<string, "PROFESIONAL_SALUD" | "ADMINISTRADOR"> = {
  "/dashboard": "PROFESIONAL_SALUD",
  "/pacientes": "PROFESIONAL_SALUD",
  "/senales": "PROFESIONAL_SALUD",
  "/admin": "ADMINISTRADOR",
};

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const requiredRole = Object.entries(ROUTE_ROLES).find(([prefix]) =>
    pathname.startsWith(prefix)
  )?.[1];

  if (!requiredRole) {
    return NextResponse.next();
  }

  const token = request.cookies.get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  if (!session) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (session.role !== requiredRole) {
    return NextResponse.redirect(new URL(roleHomePath(session.role), request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/pacientes/:path*", "/senales/:path*", "/admin/:path*"],
};
