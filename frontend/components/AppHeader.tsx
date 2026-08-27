"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { LogoutButton } from "@/components/LogoutButton";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/pacientes", label: "Pacientes" },
  { href: "/senales", label: "Señales" },
];

export function AppHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header
      style={{
        borderBottom: "1px solid var(--color-border)",
        backgroundColor: "var(--color-surface)",
        position: "relative",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "var(--space-4) var(--space-6)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)" }}>
          <Image src="/logo.png" alt="RISA Data" width={110} height={30} priority />
          <nav className="app-header-nav">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                style={{ color: "var(--color-text-secondary)", fontWeight: 600 }}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="app-header-desktop-actions">
          <LogoutButton />
        </div>

        <button
          type="button"
          className="app-header-toggle btn btn-secondary"
          aria-label={isMenuOpen ? "Cerrar menu" : "Abrir menu"}
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((prev) => !prev)}
        >
          &#8942;
        </button>
      </div>

      {isMenuOpen && (
        <div
          className="app-header-mobile-menu"
          style={{
            borderTop: "1px solid var(--color-border)",
            padding: "var(--space-4) var(--space-6)",
            flexDirection: "column",
            gap: "var(--space-4)",
          }}
        >
          <nav style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMenuOpen(false)}
                style={{ color: "var(--color-text-primary)", fontWeight: 600 }}
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <LogoutButton />
        </div>
      )}
    </header>
  );
}
