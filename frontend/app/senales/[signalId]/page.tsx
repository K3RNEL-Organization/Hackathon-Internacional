import { AppHeader } from "@/components/AppHeader";
import { SignalDetailView } from "@/components/SignalDetailView";

export default function SignalDetailPage({ params }: { params: { signalId: string } }) {
  return (
    <>
      <AppHeader />
      <main style={{ padding: "var(--space-6)", maxWidth: 900, margin: "0 auto" }}>
        <SignalDetailView signalId={params.signalId} />
      </main>
    </>
  );
}
