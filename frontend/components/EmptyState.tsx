export function EmptyState({ message }: { message: string }) {
  return (
    <div className="card state-panel">
      <p>{message}</p>
    </div>
  );
}
