from pathlib import Path
import subprocess
import sys
import time


# ============================================================
# TRIAGEMED - EJECUCION COMPLETA DEL BACKEND
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

PIPELINE = (
    PROJECT_ROOT
    / "src"
    / "risk"
    / "run_pipeline_v03.py"
)

VALIDATOR = (
    PROJECT_ROOT
    / "02_KIT_ENTREGA"
    / "validate_submission.py"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
)


def run_step(title, command):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:

        print()
        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(
            f"Falló el paso: {title}"
        )

        sys.exit(
            result.returncode
        )


# ============================================================
# INICIO
# ============================================================

start_time = time.time()

print()
print("============================================================")
print(" TRIAGEMED - BACKEND RISA V0.3")
print("============================================================")


# ============================================================
# COMPROBAR ARCHIVOS
# ============================================================

if not PIPELINE.exists():

    print(
        "ERROR: No se encontró:"
    )

    print(
        PIPELINE
    )

    sys.exit(1)


if not VALIDATOR.exists():

    print(
        "ERROR: No se encontró:"
    )

    print(
        VALIDATOR
    )

    sys.exit(1)


# ============================================================
# PASO 1 - PIPELINE
# ============================================================

run_step(
    "PASO 1/2 - EJECUTANDO MOTOR TRIAGEMED",
    [
        sys.executable,
        str(PIPELINE)
    ]
)


# ============================================================
# PASO 2 - VALIDACION OFICIAL
# ============================================================

run_step(
    "PASO 2/2 - VALIDANDO RESULTADOS",
    [
        sys.executable,
        str(VALIDATOR),
        str(RESULTS_DIR)
    ]
)


# ============================================================
# FINAL
# ============================================================

elapsed = (
    time.time()
    -
    start_time
)

print()
print("============================================================")
print(" TRIAGEMED FINALIZADO CORRECTAMENTE")
print("============================================================")

print()
print(
    "Resultados disponibles en:"
)

print(
    RESULTS_DIR
)

print(
    f"\nTiempo total: "
    f"{elapsed:.1f} segundos"
)

print()
print(
    "Backend listo para ser consumido "
    "por el dashboard."
)