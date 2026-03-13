"""
validation/historical.py — Validación contra las 23 reformas laborales 1974-2024.

Compara las predicciones del modelo (bloqueo vs. implementación) con los
resultados históricos observados de las 23 reformas laborales argentinas.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import csv
from pathlib import Path


def load_historical_reforms(csv_path: str = "data/historical_reforms.csv") -> list[dict]:
    """Carga el dataset de reformas laborales históricas.

    Args:
        csv_path: Ruta al archivo CSV.

    Returns:
        Lista de diccionarios con los datos de cada reforma.
    """
    reforms = []
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {csv_path}")

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reforms.append(row)
    return reforms


def compute_historical_block_rate(reforms: list[dict]) -> float:
    """Calcula la tasa de bloqueo histórica de las 23 reformas.

    Una reforma es 'bloqueada' si su final_outcome es 'blocked',
    'reversed', o 'partial'.

    Args:
        reforms: Lista de reformas del dataset histórico.

    Returns:
        Tasa de bloqueo histórica [0, 1].
    """
    if not reforms:
        return 0.0

    blocked_outcomes = {"blocked", "reversed", "partial"}
    n_blocked = sum(
        1 for r in reforms
        if r.get("final_outcome", "").lower() in blocked_outcomes
    )
    return n_blocked / len(reforms)


def validate_against_history(
    simulated_block_rate: float,
    csv_path: str = "data/historical_reforms.csv",
) -> dict:
    """Compara la tasa de bloqueo simulada con la histórica.

    Args:
        simulated_block_rate: Tasa de bloqueo del modelo [0, 1].
        csv_path: Ruta al CSV de reformas históricas.

    Returns:
        Diccionario con:
            - historical_block_rate: float
            - simulated_block_rate: float
            - absolute_error: float
            - n_reforms: int
            - passed: bool (error < 0.10)
    """
    try:
        reforms = load_historical_reforms(csv_path)
    except FileNotFoundError:
        return {
            "historical_block_rate": None,
            "simulated_block_rate": simulated_block_rate,
            "absolute_error": None,
            "n_reforms": 0,
            "passed": False,
            "error_message": "CSV no encontrado",
        }

    hist_rate = compute_historical_block_rate(reforms)
    error = abs(simulated_block_rate - hist_rate)

    return {
        "historical_block_rate": hist_rate,
        "simulated_block_rate": simulated_block_rate,
        "absolute_error": error,
        "n_reforms": len(reforms),
        "passed": error < 0.10,
    }


def get_reform_summary(reforms: list[dict]) -> dict:
    """Genera un resumen estadístico del dataset histórico.

    Args:
        reforms: Lista de reformas históricas.

    Returns:
        Diccionario con estadísticos del dataset.
    """
    if not reforms:
        return {}

    outcomes = {}
    union_responses = {}
    governments = {}

    for r in reforms:
        out = r.get("final_outcome", "unknown")
        outcomes[out] = outcomes.get(out, 0) + 1

        ur = r.get("union_response", "unknown")
        union_responses[ur] = union_responses.get(ur, 0) + 1

        gov = r.get("government", "unknown")
        governments[gov] = governments.get(gov, 0) + 1

    # Tiempo promedio hasta reversión (solo reformas revertidas)
    reversals = []
    for r in reforms:
        t = r.get("time_to_reversal_months", "")
        if t and t.isdigit():
            reversals.append(int(t))

    return {
        "n_total": len(reforms),
        "outcomes": outcomes,
        "union_responses": union_responses,
        "governments": governments,
        "mean_reversal_months": sum(reversals) / len(reversals) if reversals else None,
    }
