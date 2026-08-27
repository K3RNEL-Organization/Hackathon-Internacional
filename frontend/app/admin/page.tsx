import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySessionToken } from "@/lib/session";
import { LogoutButton } from "@/components/LogoutButton";

export default async function AdminPage() {
  const token = cookies().get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  return (
    <main style={{ padding: "var(--space-6)" }}>
      <h1>Área administrativa</h1>
      <p className="caption">Sesión: {session?.sub}</p>
      <p style={{ marginTop: "var(--space-4)" }}>
        Próximamente: gestión de usuarios y accesos, métricas técnicas y estado del sistema.
      </p>
      <div style={{ marginTop: "var(--space-6)" }}>
        <LogoutButton />
      </div>
    </main>
  );
}
