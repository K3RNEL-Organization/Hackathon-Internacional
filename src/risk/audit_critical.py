import pandas as pd

print("\n=== AUDITORIA DE SEÑALES CRITICAL ===")

signals = pd.read_csv(
    "results/signals.csv"
)

evidence = pd.read_csv(
    "results/evidence.csv"
)

critical = signals[
    signals["priority_level"] == "CRITICAL"
].copy()

critical = critical.sort_values(
    "risk_score",
    ascending=False
)

print("\nCantidad CRITICAL:", len(critical))


for _, signal in critical.iterrows():

    signal_id = signal["signal_id"]

    ev = evidence[
        evidence["signal_id"] == signal_id
    ]

    print("\n" + "=" * 70)

    print("Signal:", signal_id)
    print("Paciente:", signal["patient_id"])
    print("Decisión:", signal["decision_datetime"])
    print("Risk score:", signal["risk_score"])
    print("Confidence:", signal["confidence_score"])

    print("\nExplicación:")
    print(signal["explanation"])

    print("\nCantidad de evidencias:", len(ev))

    print("\nRoles:")
    print(
        ev["evidence_role"]
        .value_counts()
        .to_string()
    )

    primary = ev[
        ev["evidence_role"] == "PRIMARY"
    ]

    print("\nVariables PRIMARY:")

    print(
        primary["variable_code"]
        .value_counts()
        .to_string()
    )


print("\n=== FIN AUDITORIA ===")