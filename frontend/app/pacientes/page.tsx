import { AppHeader } from "@/components/AppHeader";

export default function PacientesPage() {
  return (
    <>
      <AppHeader />
      <main style={{ padding: "var(--space-6)", maxWidth: 1200, margin: "0 auto" }}>
        <h1>Pacientes</h1>
        <p style={{ marginTop: "var(--space-4)" }}>
          Próximamente: listado completo de pacientes, búsqueda y filtros.
        </p>
      </main>
    </>
  );
}
