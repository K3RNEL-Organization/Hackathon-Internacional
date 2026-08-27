import { AppHeader } from "@/components/AppHeader";
import { PatientDetailView } from "@/components/PatientDetailView";

export default function PatientDetailPage({ params }: { params: { patientId: string } }) {
  return (
    <>
      <AppHeader />
      <main style={{ padding: "var(--space-6)", maxWidth: 1200, margin: "0 auto" }}>
        <PatientDetailView patientId={params.patientId} />
      </main>
    </>
  );
}
