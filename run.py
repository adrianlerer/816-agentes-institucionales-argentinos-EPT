"""
816 Agentes Institucionales Argentinos: Replicación EPT

Punto de entrada único. Ejecutar:

    python run.py

Tiempo estimado: ~20 segundos
Sin dependencias externas. Sin API keys. 100% offline.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import json
import os
import sys
import time
from pathlib import Path

# ── Verificar dependencias antes de importar ────────────────────────────────
try:
    import numpy as np
    import yaml
    import matplotlib
    matplotlib.use("Agg")  # backend sin display
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"ERROR: Dependencia faltante: {e}")
    print("Instalar con: pip install -r requirements.txt")
    sys.exit(1)

# ── Agregar el directorio raíz al path para imports ─────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from engine.simulation import load_config, run_simulation
from validation.monte_carlo import run_monte_carlo, check_validation_criteria
from validation.historical import validate_against_history


def print_banner() -> None:
    """Imprime el banner de inicio."""
    print("=" * 70)
    print("816 AGENTES INSTITUCIONALES ARGENTINOS")
    print("Extended Phenotype Theory — Simulación de Reforma Laboral")
    print("Lerer (2026) | adrian@lerer.com.ar | ORCID 0009-0007-6378-9749")
    print("=" * 70)
    print()


def print_agents_summary(config: dict) -> None:
    """Imprime el resumen de agentes cargados."""
    cfg = config["agents"]
    n_judges = cfg["judges_csjn"]["count"]
    n_of = cfg["legislators_oficialismo"]["count"]
    n_op = cfg["legislators_oposicion"]["count"]
    unions = [u["name"] for u in cfg["unions"]]
    n_firms = cfg["regulated_firms"]["count"]
    n_citizens = cfg["citizens"]["count"]
    n_reg = cfg["regulator"]["count"]
    total = n_judges + n_of + n_op + len(unions) + n_firms + n_citizens + n_reg

    print(f"Agentes cargados: {total} total")
    print(f"  {n_judges} jueces CSJN (CRI={cfg['judges_csjn']['cri']})")
    print(f"  {n_of} leg. oficialismo (CRI={cfg['legislators_oficialismo']['cri']})")
    print(f"  {n_op} leg. oposición   (CRI={cfg['legislators_oposicion']['cri']})")
    print(f"  {len(unions)} sindicatos: {', '.join(unions)}")
    print(f"  {n_firms} empresas reguladas")
    print(f"  {n_citizens} ciudadanos")
    print(f"  {n_reg} regulador")
    print()


def print_mc_table(mc_results: dict) -> None:
    """Imprime la tabla de resultados Monte Carlo."""
    print("─" * 70)
    print(f"{'Seed':>6}  {'CLI Final':>10}  {'Block Rate':>10}  {'COAL+LIT':>10}  {'Pass':>4}")
    print("─" * 70)

    cli_target = 0.89
    for r in mc_results["results"]:
        cli = r["cli_final"]
        block = r["block_rate"]
        cl = r["union_coal_lit_rate"]
        # Criterio de pass: CLI en rango Y block_rate > 70%
        passed = (0.80 <= cli <= 0.95) and (block >= 0.70) and (cl >= 0.50)
        mark = "✓" if passed else "✗"
        print(
            f"{r['seed']:>6}  {cli:>10.4f}  {block:>10.1%}  {cl:>10.1%}  {mark:>4}"
        )

    print("─" * 70)
    print(
        f"{'MEDIA':>6}  {mc_results['cli_mean']:>10.4f}  "
        f"{mc_results['block_rate_mean']:>10.1%}  "
        f"{mc_results['union_coal_lit_mean']:>10.1%}"
    )
    print(f"{'  SD':>6}  {mc_results['cli_std']:>10.4f}")
    print()


def print_validation(checks: list[dict]) -> None:
    """Imprime los resultados de validación."""
    print("Validación:")
    all_passed = True
    for c in checks:
        mark = "✓" if c["passed"] else "✗"
        print(f"  {mark} {c['name']}: {c['message']}")
        if not c["passed"]:
            all_passed = False
    print()
    if all_passed:
        print("  ✓ TODOS LOS CRITERIOS CUMPLIDOS")
    else:
        print("  ✗ ADVERTENCIA: Algún criterio no cumplido. Ver docs/RESULTS.md")
    print()


def generate_plots(mc_results: dict, output_dir: Path) -> None:
    """Genera los dos gráficos de resultados.

    Args:
        mc_results: Resultados del Monte Carlo.
        output_dir: Directorio de salida para los gráficos.
    """
    seeds = mc_results["seeds"]
    results = mc_results["results"]

    # ── Gráfico 1: CLI timeseries ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, (r, seed) in enumerate(zip(results, seeds)):
        ax.plot(
            range(1, len(r["cli_history"]) + 1),
            r["cli_history"],
            alpha=0.6,
            linewidth=1.5,
            color=colors[i % len(colors)],
            label=f"Seed {seed}",
        )

    # Media
    mean_hist = mc_results["cli_history_mean"]
    ax.plot(
        range(1, len(mean_hist) + 1),
        mean_hist,
        color="black",
        linewidth=2.5,
        linestyle="--",
        label=f"Media (n=5)",
    )

    # Líneas de referencia
    ax.axhline(y=0.89, color="red", linestyle=":", alpha=0.7, label="Target CLI=0.89")
    ax.axhline(y=0.80, color="gray", linestyle=":", alpha=0.5, label="Umbral inferior")
    ax.axhline(y=0.95, color="gray", linestyle=":", alpha=0.5, label="Umbral superior")
    ax.axvline(x=5, color="orange", linestyle="--", alpha=0.7, label="Reforma (ronda 5)")

    ax.set_xlabel("Ronda")
    ax.set_ylabel("Constitutional Lock-in Index (CLI)")
    ax.set_title(
        "CLI emergente — 816 Agentes | Argentina | Reforma Laboral Flexibilizadora\n"
        "Lerer (2026) | EPT Multi-Agent Simulation"
    )
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "cli_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Gráfico 2: Distribución de acciones ─────────────────────────────
    # Sumar action_log_summary de todos los seeds
    combined: dict[str, int] = {}
    for r in results:
        for action, count in r["action_log_summary"].items():
            combined[action] = combined.get(action, 0) + count

    actions = list(combined.keys())
    counts = [combined[a] for a in actions]
    total_actions = sum(counts)
    # Normalizar a porcentaje
    pcts = [100 * c / total_actions for c in counts]

    # Colores por categoría
    action_colors = {
        "cumplir": "#2ecc71",
        "evadir": "#e74c3c",
        "litigar": "#e67e22",
        "impugnar_cn": "#c0392b",
        "reformar": "#3498db",
        "coalicionar": "#9b59b6",
        "capturar": "#95a5a6",
        "sancionar": "#f39c12",
        "reversar": "#1abc9c",
    }
    bar_colors = [action_colors.get(a.lower(), "#bdc3c7") for a in actions]

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    bars = ax2.bar(actions, pcts, color=bar_colors, edgecolor="white", linewidth=0.5)

    ax2.set_xlabel("Tipo de acción")
    ax2.set_ylabel("% del total de acciones (5 seeds × 100 rondas)")
    ax2.set_title(
        "Distribución de acciones — 816 Agentes | Argentina\n"
        "Lerer (2026) | EPT Multi-Agent Simulation"
    )

    # Etiquetas en barras
    for bar, pct in zip(bars, pcts):
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.3,
            f"{pct:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax2.tick_params(axis="x", rotation=30)
    # Alinear etiquetas a la derecha
    for tick in ax2.get_xticklabels():
        tick.set_ha("right")
    ax2.grid(True, axis="y", alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(output_dir / "action_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig2)


def save_results(mc_results: dict, checks: list[dict], output_dir: Path) -> None:
    """Guarda resultados en JSON y texto plano.

    Args:
        mc_results: Resultados del Monte Carlo.
        checks: Criterios de validación.
        output_dir: Directorio de salida.
    """
    # JSON completo
    json_output = {
        "metadata": {
            "scenario": "Flexibilización Laboral Argentina - Tipo Menem 1990s",
            "author": "Ignacio Adrián Lerer",
            "orcid": "0009-0007-6378-9749",
            "version": "1.0.0",
        },
        "summary": {
            "cli_mean": mc_results["cli_mean"],
            "cli_std": mc_results["cli_std"],
            "block_rate_mean": mc_results["block_rate_mean"],
            "union_coal_lit_mean": mc_results["union_coal_lit_mean"],
            "n_seeds": len(mc_results["seeds"]),
            "n_rounds": mc_results["n_rounds"],
        },
        "validation": [
            {k: v for k, v in c.items()} for c in checks
        ],
        "per_seed": [
            {
                "seed": r["seed"],
                "cli_final": r["cli_final"],
                "block_rate": r["block_rate"],
                "union_coal_lit_rate": r["union_coal_lit_rate"],
                "reform_attempts": r["reform_attempts"],
                "reform_blocked": r["reform_blocked"],
            }
            for r in mc_results["results"]
        ],
    }

    with open(output_dir / "monte_carlo_results.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)

    # Resumen en texto plano
    lines = [
        "816 AGENTES INSTITUCIONALES ARGENTINOS",
        "Extended Phenotype Theory — Simulación de Reforma Laboral",
        "Lerer (2026) | AGPL-3.0",
        "",
        "RESUMEN DE RESULTADOS",
        "=" * 50,
        f"CLI medio (5 seeds):     {mc_results['cli_mean']:.4f}",
        f"CLI desv. estándar:      {mc_results['cli_std']:.4f}",
        f"Tasa bloqueo media:      {mc_results['block_rate_mean']:.1%}",
        f"COAL+LIT sindical media: {mc_results['union_coal_lit_mean']:.1%}",
        "",
        "VALIDACIÓN",
        "=" * 50,
    ]
    for c in checks:
        mark = "✓" if c["passed"] else "✗"
        lines.append(f"{mark} {c['name']}: {c['message']}")

    lines += [
        "",
        "Generado por: python run.py",
        "Repositorio: github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT",
    ]

    with open(output_dir / "summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    """Función principal. Retorna 0 si todos los criterios pasan, 1 si no."""
    t_start = time.time()

    # ── 1. Banner ────────────────────────────────────────────────────────
    print_banner()

    # ── 2. Cargar configuración ──────────────────────────────────────────
    config_path = ROOT / "config" / "argentina.yaml"
    if not config_path.exists():
        print(f"ERROR: No se encontró {config_path}")
        return 1

    config = load_config(str(config_path))
    scenario = config["scenario"]
    print(f"Escenario: {scenario['name']}")
    print(f"CLI target: {scenario['cli_target']} | Rondas: {scenario['simulation_rounds']}")
    print(f"Seeds: {scenario['monte_carlo_seeds']}")
    print()

    # ── 3. Resumen de agentes ────────────────────────────────────────────
    print_agents_summary(config)

    # ── 4. Monte Carlo: 5 seeds × 100 rondas ────────────────────────────
    print(f"Corriendo Monte Carlo ({len(scenario['monte_carlo_seeds'])} seeds × "
          f"{scenario['simulation_rounds']} rondas)...")
    print()

    mc_results = run_monte_carlo(
        config,
        n_rounds=scenario["simulation_rounds"],
        print_progress=True,
    )
    print()

    # ── 5. Tabla de resultados ───────────────────────────────────────────
    print_mc_table(mc_results)

    # ── 6. Validación ────────────────────────────────────────────────────
    checks = check_validation_criteria(
        mc_results,
        config["validation_criteria"],
        cli_target=scenario["cli_target"],
    )
    print_validation(checks)

    # ── 7. Gráficos ──────────────────────────────────────────────────────
    output_dir = ROOT / "results"
    output_dir.mkdir(exist_ok=True)

    print("Generando gráficos...", end="", flush=True)
    generate_plots(mc_results, output_dir)
    print(f" Guardados en results/")
    print("  → results/cli_timeseries.png")
    print("  → results/action_distribution.png")
    print()

    # ── 8. Guardar resultados ────────────────────────────────────────────
    save_results(mc_results, checks, output_dir)
    print("Datos guardados:")
    print("  → results/monte_carlo_results.json")
    print("  → results/summary.txt")
    print()

    # ── 9. Footer ────────────────────────────────────────────────────────
    t_elapsed = time.time() - t_start
    all_passed = all(c["passed"] for c in checks)

    print("=" * 70)
    print("REPLICACIÓN COMPLETADA")
    print(f"Tiempo: {t_elapsed:.1f}s")
    print(f"Resultados en: results/")
    print(f"Paper: Lerer (2026) DOI: [pending]")
    print(f"Repo principal: github.com/adrianlerer/legal-evolution-unified")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
