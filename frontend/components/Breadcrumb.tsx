import Link from "next/link";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="breadcrumb" aria-label="Ruta de navegación">
      {items.map((item, index) => (
        <span key={index} style={{ display: "inline-flex", alignItems: "center", gap: "var(--space-2)" }}>
          {index > 0 && (
            <span className="breadcrumb__separator" aria-hidden="true">
              ›
            </span>
          )}
          {item.href ? (
            <Link href={item.href}>{item.label}</Link>
          ) : (
            <span className="breadcrumb__current" aria-current="page">
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
