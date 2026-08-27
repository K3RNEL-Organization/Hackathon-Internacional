"use client";

import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      style={{
        marginTop: "var(--space-6)",
        padding: "var(--space-2) var(--space-4)",
        borderRadius: "var(--radius-sm)",
        border: "1px solid var(--color-border)",
        backgroundColor: "var(--color-surface)",
        color: "var(--color-text-primary)",
        fontSize: 13,
        cursor: "pointer",
      }}
    >
      Cerrar sesion
    </button>
  );
}
