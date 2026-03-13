"""
validation/monte_carlo.py — Validación Monte Carlo (5 seeds × 100 rondas).

Corre la simulación con los 5 seeds especificados en la configuración
y verifica que los resultados caen dentro de los criterios publicados.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import numpy as np
from engine.simulation import run_simulation, load_config


def run_monte_carlo(
    config: dict,
    n_rounds: int = 100,
    print_progress: bool = True,
) -> dict:
    """Ejecuta la validación Monte Carlo con los seeds de la configuración.

    Args:
        config: Configuración del escenario (cargado desde argentina.yaml).
        n_rounds: Número de rondas por seed.
        print_progress: Si True, imprime progreso de cada seed.

    Returns:
        Diccionario con resultados aggregados:
            - results: lista de resultados por seed
            - cli_mean: media del CLI final
            - cli_std: desviación estándar del CLI final
            - cli_history_mean: serie temporal media (array numpy)
            - block_rate_mean: tasa de bloqueo media
            - union_coal_lit_mean: tasa COAL+LIT media
            - seeds: lista de seeds usados
    """
    seeds = config["scenario"]["monte_carlo_seeds"]
    results = []

    for seed in seeds:
        if print_progress:
            print(f"  Seed {seed}: corriendo {n_rounds} rondas...", end="", flush=True)

        result = run_simulation(config, seed=seed, n_rounds=n_rounds, verbose=False)
        results.append(result)

        if print_progress:
            print(
                f" CLI={result['cli_final']:.4f}, "
                f"block={result['block_rate']:.1%}, "
                f"COAL+LIT={result['union_coal_lit_rate']:.1%}"
            )

    # Calcular estadísticos agregados
    cli_finals = [r["cli_final"] for r in results]
    block_rates = [r["block_rate"] for r in results]
    coal_lit_rates = [r["union_coal_lit_rate"] for r in results]

    # Serie temporal media (todas las runs tienen n_rounds valores)
    cli_histories = np.array([r["cli_history"] for r in results])
    cli_history_mean = cli_histories.mean(axis=0).tolist()

    return {
        "results": results,
        "cli_mean": float(np.mean(cli_finals)),
        "cli_std": float(np.std(cli_finals)),
        "cli_history_mean": cli_history_mean,
        "block_rate_mean": float(np.mean(block_rates)),
        "union_coal_lit_mean": float(np.mean(coal_lit_rates)),
        "seeds": seeds,
        "n_rounds": n_rounds,
    }


def check_validation_criteria(
    mc_results: dict,
    criteria: dict,
    cli_target: float = 0.89,
) -> list[dict]:
    """Verifica los 4 criterios de validación publicados.

    Args:
        mc_results: Resultados del Monte Carlo (output de run_monte_carlo).
        criteria: Diccionario de criterios (de argentina.yaml).
        cli_target: CLI objetivo de la calibración histórica.

    Returns:
        Lista de 4 diccionarios con:
            - name: nombre del criterio
            - value: valor observado
            - threshold: umbral requerido
            - passed: bool
            - message: descripción del resultado
    """
    checks = []
    cli_mean = mc_results["cli_mean"]
    block_rate = mc_results["block_rate_mean"]
    coal_lit = mc_results["union_coal_lit_mean"]

    # 1. CLI en rango [0.80, 0.95]
    cli_range = criteria["cli_range"]
    in_range = cli_range[0] <= cli_mean <= cli_range[1]
    checks.append({
        "name": "CLI ∈ [0.80, 0.95]",
        "value": cli_mean,
        "threshold": f"[{cli_range[0]}, {cli_range[1]}]",
        "passed": in_range,
        "message": (
            f"mean={cli_mean:.4f} "
            f"({'✓' if in_range else '✗'})"
        ),
    })

    # 2. Tasa de bloqueo > 70%
    min_block = criteria["min_block_rate"]
    block_ok = block_rate >= min_block
    checks.append({
        "name": "Reform block rate >70%",
        "value": block_rate,
        "threshold": f">{min_block:.0%}",
        "passed": block_ok,
        "message": f"{block_rate:.1%} ({'✓' if block_ok else '✗'})",
    })

    # 3. Sindicatos COAL+LIT > 50%
    min_cl = criteria["min_union_coalition_litigate"]
    cl_ok = coal_lit >= min_cl
    checks.append({
        "name": "Union COALICIONAR+LITIGAR >50%",
        "value": coal_lit,
        "threshold": f">{min_cl:.0%}",
        "passed": cl_ok,
        "message": f"{coal_lit:.1%} ({'✓' if cl_ok else '✗'})",
    })

    # 4. Error de calibración < 5%
    cli_error = abs(cli_mean - cli_target)
    max_error = criteria["max_cli_error"]
    error_ok = cli_error <= max_error
    checks.append({
        "name": "CLI calibration accuracy",
        "value": cli_error,
        "threshold": f"error < {max_error}",
        "passed": error_ok,
        "message": (
            f"error={cli_error:.3f} < threshold {max_error} "
            f"({'✓' if error_ok else '✗'})"
        ),
    })

    return checks
