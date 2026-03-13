"""
validation/emergent_cli.py — Verificación de CLI emergente sin target injection.

Confirma que el CLI observado (≈0.92) EMERGE de las interacciones
entre agentes, no está pre-programado como valor objetivo.

El test clave: correr el modelo con CLI target=0.0 y verificar que
igual converge al mismo atractor (~0.92). Si el resultado cambia,
habría target injection.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import copy
from engine.simulation import run_simulation


def verify_emergent_cli(
    config: dict,
    seed: int = 42,
    n_rounds: int = 100,
    tolerance: float = 0.05,
) -> dict:
    """Verifica que el CLI emerge sin depender del target en la config.

    Corre dos simulaciones:
    1. Config original (cli_target=0.89)
    2. Config modificada (cli_target=0.0 — sin objetivo)

    Si ambas producen CLI similares (dentro de la tolerancia), el
    valor es genuinamente emergente.

    Args:
        config: Configuración original del escenario.
        seed: Semilla para reproducibilidad.
        n_rounds: Rondas de simulación.
        tolerance: Diferencia máxima de CLI aceptable entre runs.

    Returns:
        Diccionario con:
            - cli_with_target: CLI con configuración original
            - cli_without_target: CLI con target=0.0
            - difference: diferencia absoluta
            - is_emergent: bool (True si diferencia < tolerance)
            - message: descripción del resultado
    """
    # Run 1: configuración original
    result_original = run_simulation(config, seed=seed, n_rounds=n_rounds)
    cli_original = result_original["cli_final"]

    # Run 2: configuración con target neutralizado
    config_no_target = copy.deepcopy(config)
    config_no_target["scenario"]["cli_target"] = 0.0
    result_no_target = run_simulation(config_no_target, seed=seed, n_rounds=n_rounds)
    cli_no_target = result_no_target["cli_final"]

    diff = abs(cli_original - cli_no_target)
    is_emergent = diff < tolerance

    return {
        "cli_with_target": cli_original,
        "cli_without_target": cli_no_target,
        "difference": diff,
        "tolerance": tolerance,
        "is_emergent": is_emergent,
        "message": (
            f"CLI(target=0.89)={cli_original:.4f} vs "
            f"CLI(target=0.0)={cli_no_target:.4f} — "
            f"diff={diff:.4f} "
            f"{'< tolerance → EMERGENTE ✓' if is_emergent else '≥ tolerance → WARNING'}"
        ),
    }


def run_sensitivity_analysis(
    config: dict,
    param_name: str,
    param_values: list[float],
    seed: int = 42,
    n_rounds: int = 50,
) -> list[dict]:
    """Análisis de sensibilidad: varía un parámetro y observa el CLI resultante.

    Útil para entender qué parámetros son más influyentes en el CLI
    emergente.

    Args:
        config: Configuración base.
        param_name: Nombre del parámetro a variar (ej: 'judges_csjn.cri').
        param_values: Lista de valores a probar.
        seed: Semilla para reproducibilidad.
        n_rounds: Rondas por simulación.

    Returns:
        Lista de resultados para cada valor del parámetro.
    """
    import copy

    results = []
    for value in param_values:
        cfg = copy.deepcopy(config)

        # Navegar la ruta del parámetro (ej: 'agents.judges_csjn.cri')
        parts = param_name.split(".")
        node = cfg
        for part in parts[:-1]:
            node = node[part]
        node[parts[-1]] = value

        result = run_simulation(cfg, seed=seed, n_rounds=n_rounds)
        results.append({
            "param_name": param_name,
            "param_value": value,
            "cli_final": result["cli_final"],
            "block_rate": result["block_rate"],
        })

    return results
