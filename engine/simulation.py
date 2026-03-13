"""
engine/simulation.py — Motor de simulación principal.

10 pasos por ronda × 100 rondas × 816 agentes.
Cada ronda:
  1. Iniciar ronda (trigger reforma si aplica)
  2. Actualizar n_supporters de todos los agentes
  3. Cada agente decide su acción
  4. Aplicar acciones al entorno
  5. Procesar capturas (regulador)
  6. HBU update para todos los agentes
  7. Actualizar n_supporters post-acción
  8. Computar CLI
  9. Computar métricas parciales
  10. Registrar estado

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
import json
from pathlib import Path

import yaml

from agents.judge import JudgeAgent
from agents.legislator import LegislatorAgent
from agents.union import UnionAgent
from agents.firm import RegulatedFirmAgent
from agents.citizen import CitizenAgent
from agents.regulator import RegulatorAgent
from engine.actions import ActionType
from engine.environment import LegalEnvironment
from engine.hbu import hbu_batch_update


def load_config(config_path: str = "config/argentina.yaml") -> dict:
    """Carga la configuración del escenario desde YAML.

    Args:
        config_path: Ruta al archivo de configuración.

    Returns:
        Diccionario de configuración.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_agents(config: dict, rng: random.Random) -> list:
    """Instancia los 816 agentes desde la configuración y el JSON de parámetros.

    Args:
        config: Configuración del escenario.
        rng: Generador aleatorio con seed controlada.

    Returns:
        Lista de todos los agentes instanciados.
    """
    agents = []
    cfg = config["agents"]

    # 1. Jueces CSJN (5)
    jcfg = cfg["judges_csjn"]
    for i in range(jcfg["count"]):
        agents.append(JudgeAgent(
            agent_id=f"judge_{i}",
            cri=jcfg["cri"],
            institutional_capital=jcfg["institutional_capital"],
            rng=rng,
        ))

    # 2. Legisladores oficialismo (130)
    lcfg = cfg["legislators_oficialismo"]
    for i in range(lcfg["count"]):
        agents.append(LegislatorAgent(
            agent_id=f"leg_of_{i}",
            cri=lcfg["cri"],
            institutional_capital=lcfg["institutional_capital"],
            party_discipline=lcfg["party_discipline"],
            reform_preference=lcfg["reform_preference"],
            is_oficialismo=True,
            rng=rng,
        ))

    # 3. Legisladores oposición (127)
    ocfg = cfg["legislators_oposicion"]
    for i in range(ocfg["count"]):
        agents.append(LegislatorAgent(
            agent_id=f"leg_op_{i}",
            cri=ocfg["cri"],
            institutional_capital=ocfg["institutional_capital"],
            party_discipline=ocfg["party_discipline"],
            reform_preference=ocfg["reform_preference"],
            is_oficialismo=False,
            rng=rng,
        ))

    # 4. Sindicatos (3: CGT, CTA, Sectorial)
    for union_cfg in cfg["unions"]:
        action_names = union_cfg["actions"]
        actions = [ActionType[a] for a in action_names]
        # Parámetros opcionales
        strike_cap = union_cfg.get("strike_capacity", 0.60)
        legal_res = union_cfg.get("legal_resources", 0.60)
        agents.append(UnionAgent(
            agent_id=f"union_{union_cfg['name'].lower()}",
            union_name=union_cfg["name"],
            cri=union_cfg["cri"],
            institutional_capital=union_cfg["institutional_capital"],
            coalition_capacity=union_cfg["coalition_capacity"],
            strike_capacity=strike_cap,
            legal_resources=legal_res,
            available_actions=actions,
            rng=rng,
        ))

    # 5. Empresas reguladas (50)
    fcfg = cfg["regulated_firms"]
    for i in range(fcfg["count"]):
        agents.append(RegulatedFirmAgent(
            agent_id=f"firm_{i}",
            cri=fcfg["cri"],
            institutional_capital=fcfg["institutional_capital"],
            capture_capacity=fcfg["capture_capacity"],
            rng=rng,
        ))

    # 6. Ciudadanos (500)
    ccfg = cfg["citizens"]
    for i in range(ccfg["count"]):
        agents.append(CitizenAgent(
            agent_id=f"citizen_{i}",
            cri=ccfg["cri"],
            institutional_capital=ccfg["institutional_capital"],
            coalition_capacity=ccfg["coalition_capacity"],
            rng=rng,
        ))

    # 7. Regulador (1)
    rcfg = cfg["regulator"]
    agents.append(RegulatorAgent(
        agent_id="regulator_0",
        cri=rcfg["cri"],
        institutional_capital=rcfg["institutional_capital"],
        capture_vulnerability=rcfg["capture_vulnerability"],
        rng=rng,
    ))

    return agents


def _update_n_supporters(agents: list) -> None:
    """Actualiza n_supporters de cada agente contando agentes del mismo tipo.

    Args:
        agents: Lista completa de agentes.
    """
    type_counts: dict[str, int] = {}
    for agent in agents:
        key = agent.agent_type
        type_counts[key] = type_counts.get(key, 0) + 1

    for agent in agents:
        # n_supporters = compañeros del mismo tipo (excluye al agente mismo)
        agent.n_supporters = type_counts.get(agent.agent_type, 1) - 1


def run_simulation(
    config: dict,
    seed: int,
    n_rounds: int = 100,
    verbose: bool = False,
) -> dict:
    """Ejecuta una simulación completa con un seed dado.

    Implementa los 10 pasos por ronda del modelo EPT.

    Args:
        config: Configuración del escenario.
        seed: Semilla aleatoria para reproducibilidad.
        n_rounds: Número de rondas a simular.
        verbose: Si True, imprime progreso de cada ronda.

    Returns:
        Diccionario con resultados:
            - seed: int
            - cli_final: float
            - cli_history: list[float]
            - block_rate: float
            - union_coal_lit_rate: float
            - reform_attempts: int
            - reform_blocked: int
            - action_log_summary: dict
    """
    rng = random.Random(seed)

    # Instanciar agentes y entorno
    agents = build_agents(config, rng)
    env = LegalEnvironment(config, rng=rng)

    # Paso 0: inicializar n_supporters
    _update_n_supporters(agents)

    # Separar regulador para tratamiento especial
    regulators = [a for a in agents if isinstance(a, RegulatorAgent)]
    firms = [a for a in agents if isinstance(a, RegulatedFirmAgent)]

    # ── Bucle principal: 100 rondas ──────────────────────────────────────
    for round_num in range(1, n_rounds + 1):

        # Paso 1: iniciar ronda (trigger reforma)
        env.start_round(round_num)

        # Paso 2: tick captura en regulador
        for reg in regulators:
            reg.tick_capture()

        # Paso 3: procesar intentos de captura de empresas
        for firm in firms:
            if env.reform_active:
                action = firm.decide_action(env)
                if action == ActionType.CAPTURAR:
                    for reg in regulators:
                        reg.receive_capture_attempt(firm.capture_capacity)

        # Paso 4: cada agente decide su acción (en orden de CRI descendente)
        # Los agentes con mayor CRI actúan primero (mayor poder institucional)
        ordered_agents = sorted(agents, key=lambda a: -a.cri)
        for agent in ordered_agents:
            action = agent.decide_action(env)
            # Regulador capturado: SANCIONAR sin efecto
            if isinstance(agent, RegulatorAgent) and agent.is_captured:
                continue
            env.apply_action(agent.agent_id, agent.agent_type, action)

        # Paso 5: HBU update para todos los agentes
        hbu_batch_update(agents, env.sanctions_this_round)

        # Paso 6: actualizar n_supporters (coaliciones pueden cambiar)
        _update_n_supporters(agents)

        # Paso 7: computar CLI de esta ronda
        cli = env.compute_current_cli()

        # Paso 8: ajuste de coalition_strength (decae si no hay COALICIONAR)
        recent_coal = sum(
            1 for r in env.action_log[-len(agents):]
            if r["action"] == ActionType.COALICIONAR
        )
        if recent_coal == 0:
            env.coalition_strength = max(0.0, env.coalition_strength - 0.02)

        if verbose:
            block_rate = env.get_block_rate()
            print(
                f"  Ronda {round_num:3d}/100  CLI={cli:.4f}  "
                f"block={block_rate:.1%}  coal={env.coalition_strength:.2f}"
            )

    # ── Calcular métricas finales ────────────────────────────────────────
    from engine.metrics import compute_union_coal_lit_rate

    cli_final = env.cli_history[-1] if env.cli_history else 0.0
    block_rate = env.get_block_rate()
    union_coal_lit = compute_union_coal_lit_rate(env.action_log)

    # Resumen de distribución de acciones
    action_summary: dict[str, int] = {}
    for record in env.action_log:
        key = record["action"].value
        action_summary[key] = action_summary.get(key, 0) + 1

    return {
        "seed": seed,
        "cli_final": cli_final,
        "cli_history": env.cli_history,
        "block_rate": block_rate,
        "union_coal_lit_rate": union_coal_lit,
        "reform_attempts": env.reform_attempts,
        "reform_blocked": env.reform_blocked,
        "action_log_summary": action_summary,
        "total_rounds": n_rounds,
    }
