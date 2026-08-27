import { AppHeader } from "@/components/AppHeader";
import { SignalsView } from "@/components/SignalsView";

export default function SenalesPage() {
  return (
    <>
      <AppHeader />
      <main style={{ padding: "var(--space-6)", maxWidth: 1200, margin: "0 auto" }}>
        <SignalsView />
      </main>
    </>
  );
}
