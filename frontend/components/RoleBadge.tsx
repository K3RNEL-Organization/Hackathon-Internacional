const ROLE_CLASS: Record<string, string> = {
  PRIMARY: "role-badge--primary",
  SUPPORTING: "role-badge--supporting",
  CONTEXT: "role-badge--context",
  QUALITY: "role-badge--quality",
};

const ROLE_LABEL: Record<string, string> = {
  PRIMARY: "Primaria",
  SUPPORTING: "De apoyo",
  CONTEXT: "Contexto",
  QUALITY: "Calidad",
};

/** Visual badge for evidence_role. The underlying value is never changed, only styled. */
export function RoleBadge({ role }: { role: string }) {
  return (
    <span className={`role-badge ${ROLE_CLASS[role] ?? "role-badge--context"}`} title={role}>
      {ROLE_LABEL[role] ?? role}
    </span>
  );
}
