"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface FieldErrors {
  email?: string;
  password?: string;
}

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const errors: FieldErrors = {};

    if (!email.trim()) {
      errors.email = "El correo es obligatorio.";
    } else if (!EMAIL_PATTERN.test(email.trim())) {
      errors.email = "Ingrese un correo electrónico válido.";
    }

    if (!password) {
      errors.password = "La contraseña es obligatoria.";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 401) {
        setFormError("Credenciales incorrectas.");
        return;
      }

      if (!response.ok) {
        setFormError("No fue posible iniciar sesión. Intente nuevamente.");
        return;
      }

      const homePath = data.role === "ADMINISTRADOR" ? "/admin" : "/dashboard";
      router.push(homePath);
      router.refresh();
    } catch {
      setFormError("No fue posible iniciar sesión. Intente nuevamente.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      style={{
        width: "100%",
        maxWidth: 400,
        backgroundColor: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-6)",
        boxShadow: "0 1px 3px rgba(15, 23, 42, 0.06)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "center", marginBottom: "var(--space-5)" }}>
        <Image src="/logo-light.png" alt="RISA Data" width={200} height={47} priority />
      </div>

      <h1 style={{ fontSize: 20, textAlign: "center", marginBottom: "var(--space-1)" }}>
        Iniciar sesión
      </h1>
      <p
        className="caption"
        style={{ textAlign: "center", marginBottom: "var(--space-5)" }}
      >
        Accede al panel clínico de señales de riesgo
      </p>

      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="email" style={labelStyle}>
            Correo electrónico
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={Boolean(fieldErrors.email)}
            aria-describedby={fieldErrors.email ? "email-error" : undefined}
            style={inputStyle(Boolean(fieldErrors.email))}
          />
          {fieldErrors.email && (
            <p id="email-error" role="alert" style={errorTextStyle}>
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div style={{ marginBottom: "var(--space-5)" }}>
          <label htmlFor="password" style={labelStyle}>
            Contraseña
          </label>
          <div style={{ position: "relative" }}>
            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              aria-invalid={Boolean(fieldErrors.password)}
              aria-describedby={fieldErrors.password ? "password-error" : undefined}
              style={{ ...inputStyle(Boolean(fieldErrors.password)), paddingRight: 72 }}
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              style={toggleButtonStyle}
            >
              {showPassword ? "Ocultar" : "Mostrar"}
            </button>
          </div>
          {fieldErrors.password && (
            <p id="password-error" role="alert" style={errorTextStyle}>
              {fieldErrors.password}
            </p>
          )}
        </div>

        {formError && (
          <div
            role="alert"
            style={{
              backgroundColor: "var(--color-error-bg)",
              color: "var(--color-error)",
              borderRadius: "var(--radius-sm)",
              padding: "var(--space-3) var(--space-4)",
              marginBottom: "var(--space-4)",
              fontSize: 13,
            }}
          >
            {formError}
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            width: "100%",
            padding: "var(--space-3) var(--space-4)",
            borderRadius: "var(--radius-sm)",
            border: "none",
            backgroundColor: isSubmitting ? "var(--color-action-hover)" : "var(--color-action)",
            color: "#ffffff",
            fontSize: 14,
            fontWeight: 600,
            cursor: isSubmitting ? "not-allowed" : "pointer",
            transition: "background-color 0.15s ease",
          }}
        >
          {isSubmitting ? "Ingresando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 13,
  fontWeight: 600,
  color: "var(--color-text-primary)",
  marginBottom: "var(--space-2)",
};

function inputStyle(hasError: boolean): React.CSSProperties {
  return {
    width: "100%",
    padding: "var(--space-3)",
    borderRadius: "var(--radius-sm)",
    border: `1px solid ${hasError ? "var(--color-error)" : "var(--color-border)"}`,
    fontSize: 14,
    color: "var(--color-text-primary)",
    outline: "none",
  };
}

const errorTextStyle: React.CSSProperties = {
  color: "var(--color-error)",
  fontSize: 12,
  marginTop: "var(--space-1)",
  marginBottom: 0,
};

const toggleButtonStyle: React.CSSProperties = {
  position: "absolute",
  right: "var(--space-2)",
  top: "50%",
  transform: "translateY(-50%)",
  border: "none",
  background: "transparent",
  color: "var(--color-action)",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
  padding: "var(--space-1) var(--space-2)",
};
