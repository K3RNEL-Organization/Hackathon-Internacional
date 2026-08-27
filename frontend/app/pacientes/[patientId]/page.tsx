import { AppShell } from "@/components/AppShell";
import { PatientDetailView } from "@/components/PatientDetailView";

export default function PatientDetailPage({ params }: { params: { patientId: string } }) {
  return (
    <AppShell>
      <PatientDetailView patientId={params.patientId} />
    </AppShell>
  );
}
