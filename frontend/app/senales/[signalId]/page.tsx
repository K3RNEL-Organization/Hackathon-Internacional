import { AppShell } from "@/components/AppShell";
import { SignalDetailView } from "@/components/SignalDetailView";

export default function SignalDetailPage({ params }: { params: { signalId: string } }) {
  return (
    <AppShell>
      <SignalDetailView signalId={params.signalId} />
    </AppShell>
  );
}
