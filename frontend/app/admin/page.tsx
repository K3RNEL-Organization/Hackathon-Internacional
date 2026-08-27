import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySessionToken } from "@/lib/session";
import { LogoutButton } from "@/components/LogoutButton";

export default async function AdminPage() {
  const token = cookies().get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  return (
    <main style={{ padding: "var(--space-6)" }}>
      <h1>Area administrativa</h1>
      <p className="caption">Sesion: {session?.sub}</p>
      <p style={{ marginTop: "var(--space-4)" }}>
        Proximamente: gestion de usuarios y accesos, metricas tecnicas y estado del sistema.
      </p>
      <LogoutButton />
    </main>
  );
}
