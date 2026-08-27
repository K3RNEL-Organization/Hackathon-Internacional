import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SESSION_COOKIE, roleHomePath, verifySessionToken } from "@/lib/session";
import { LoginForm } from "@/components/LoginForm";

export default async function LoginPage() {
  const token = cookies().get(SESSION_COOKIE)?.value;
  const session = token ? await verifySessionToken(token) : null;

  if (session) {
    redirect(roleHomePath(session.role));
  }

  return (
    <main
      style={{
        minHeight: "100dvh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--space-5)",
        backgroundColor: "var(--color-background)",
      }}
    >
      <LoginForm />
    </main>
  );
}
