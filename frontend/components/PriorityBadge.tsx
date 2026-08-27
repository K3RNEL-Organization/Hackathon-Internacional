import { PRIORITY_LABEL, Priority } from "@/lib/types";

const DOT_CLASS: Record<Priority, string> = {
  LOW: "priority-low",
  MEDIUM: "priority-medium",
  HIGH: "priority-high",
  CRITICAL: "priority-critical",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className="priority-badge" aria-label={`Prioridad ${PRIORITY_LABEL[priority].toLowerCase()}`}>
      <span className={`priority-indicator ${DOT_CLASS[priority]}`} aria-hidden="true" />
      {PRIORITY_LABEL[priority]}
    </span>
  );
}
