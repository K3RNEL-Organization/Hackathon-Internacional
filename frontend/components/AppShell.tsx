"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { CurrentUser } from "@/lib/types";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: "◈" },
  { href: "/pacientes", label: "Pacientes", icon: "⌁" },
  { href: "/senales", label: "Señales", icon: "▥" },
];

const ROLE_DISPLAY_LABEL: Record<CurrentUser["role"], string> = {
  PROFESIONAL_SALUD: "Martina Gómez",
  ADMINISTRADOR: "Administrador",
};

const ROLE_AVATAR_LABEL: Record<CurrentUser["role"], string> = {
  PROFESIONAL_SALUD: "MG",
  ADMINISTRADOR: "AD",
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/auth/me", { cache: "no-store" })
      .then((response) => {
        if (response.status === 401) {
          router.push("/login");
          return null;
        }
        return response.ok ? response.json() : null;
      })
      .then((data) => {
        if (!cancelled && data) setUser(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  const showProfessionalNav = !user || user.role === "PROFESIONAL_SALUD";

  return (
    <div className="app-shell">
      <div
        className={`sidebar__overlay ${isSidebarOpen ? "sidebar__overlay--open" : ""}`}
        onClick={() => setIsSidebarOpen(false)}
      />
      <aside className={`sidebar ${isSidebarOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__brand">
          <Image src="/logo.png" alt="RISA Data" width={150} height={35} priority />
        </div>

        {showProfessionalNav && (
          <nav className="sidebar__nav" aria-label="Navegación principal">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`sidebar__link ${pathname?.startsWith(link.href) ? "sidebar__link--active" : ""}`}
                onClick={() => setIsSidebarOpen(false)}
              >
                <span aria-hidden="true">{link.icon}</span> {link.label}
              </Link>
            ))}
          </nav>
        )}

        <div className="sidebar__footer">
          <div style={{ position: "relative" }}>
            <button
              type="button"
              className="sidebar__profile"
              onClick={() => setIsProfileOpen((prev) => !prev)}
              aria-expanded={isProfileOpen}
              aria-label="Abrir menú de perfil"
            >
              <span className="avatar">{user ? ROLE_AVATAR_LABEL[user.role] : "…"}</span>
              <span>
                <strong style={{ display: "block", fontSize: 13 }}>
                  {user ? ROLE_DISPLAY_LABEL[user.role] : "Cargando..."}
                </strong>
              </span>
            </button>

            {isProfileOpen && (
              <div
                className="card"
                style={{
                  position: "absolute",
                  bottom: "calc(100% + 8px)",
                  left: 0,
                  right: 0,
                  padding: "var(--space-3)",
                  zIndex: 30,
                }}
              >
                <button type="button" className="btn btn-secondary" style={{ width: "100%" }} onClick={handleLogout}>
                  Cerrar sesión
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <button
            type="button"
            className="icon-button topbar__menu-button"
            aria-label="Abrir navegación"
            onClick={() => setIsSidebarOpen(true)}
          >
            ☰
          </button>
          <div />
        </header>

        <main style={{ padding: "var(--space-6)", maxWidth: 1200, margin: "0 auto" }}>{children}</main>
      </div>
    </div>
  );
}
