import { cookies } from "next/headers";
import { SESSION_COOKIE, verifySessionToken } from "@/lib/session";
import { LogoutButton } from "@/components/LogoutButton";

export default async function DashboardPage() {
  const token = cookies().get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  return (
    <main style={{ padding: "var(--space-6)" }}>
      <h1>Dashboard clinico</h1>
      <p className="caption">Sesion: {session?.sub}</p>
      <p style={{ marginTop: "var(--space-4)" }}>
        Proximamente: estado general, casos activos, distribucion por prioridad y senales
        recientes.
      </p>
      <LogoutButton />
    </main>
  );
}
