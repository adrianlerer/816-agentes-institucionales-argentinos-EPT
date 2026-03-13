"""
engine/actions.py — Tipos de acciones y costos.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

from enum import Enum


class ActionType(Enum):
    """Nueve acciones disponibles en el sistema institucional.

    Cada acción tiene un costo (en capital institucional) y está
    restringida a ciertos tipos de agentes según su rol.
    """

    CUMPLIR = "cumplir"
    EVADIR = "evadir"
    LITIGAR = "litigar"
    IMPUGNAR_CN = "impugnar_cn"
    REFORMAR = "reformar"
    COALICIONAR = "coalicionar"
    CAPTURAR = "capturar"
    SANCIONAR = "sancionar"
    REVERSAR = "reversar"


# Costo base de cada acción (fracción del capital institucional consumido)
ACTION_COSTS: dict[ActionType, float] = {
    ActionType.CUMPLIR: 0.05,
    ActionType.EVADIR: 0.15,
    ActionType.LITIGAR: 0.40,
    ActionType.IMPUGNAR_CN: 0.60,
    ActionType.REFORMAR: 0.50,
    ActionType.COALICIONAR: 0.25,
    ActionType.CAPTURAR: 0.70,
    ActionType.SANCIONAR: 0.30,
    ActionType.REVERSAR: 0.55,
}

# Efecto sobre el CLI de cada acción (positivo = aumenta rigidez)
# Valores pequeños para evitar saturación: los componentes deben
# oscilar en [0.75, 0.95] para producir CLI ~0.92 al agregar.
ACTION_CLI_EFFECT: dict[ActionType, float] = {
    ActionType.CUMPLIR: +0.002,
    ActionType.EVADIR: -0.002,
    ActionType.LITIGAR: +0.005,
    ActionType.IMPUGNAR_CN: +0.008,
    ActionType.REFORMAR: -0.006,
    ActionType.COALICIONAR: +0.006,
    ActionType.CAPTURAR: -0.003,
    ActionType.SANCIONAR: +0.003,
    ActionType.REVERSAR: -0.008,
}

# Acciones que constituyen resistencia activa a la reforma
RESISTANCE_ACTIONS: set[ActionType] = {
    ActionType.LITIGAR,
    ActionType.IMPUGNAR_CN,
    ActionType.COALICIONAR,
    ActionType.REVERSAR,
    ActionType.SANCIONAR,
}

# Acciones que facilitan la reforma
REFORM_ACTIONS: set[ActionType] = {
    ActionType.REFORMAR,
    ActionType.CUMPLIR,
    ActionType.CAPTURAR,
}


def get_action_cost(action: ActionType) -> float:
    """Devuelve el costo base de una acción.

    Args:
        action: Tipo de acción.

    Returns:
        Costo base como fracción [0, 1].
    """
    return ACTION_COSTS[action]


def get_cli_effect(action: ActionType) -> float:
    """Devuelve el efecto de una acción sobre el CLI.

    Args:
        action: Tipo de acción.

    Returns:
        Delta CLI (positivo = más rigidez, negativo = menos rigidez).
    """
    return ACTION_CLI_EFFECT[action]


def is_resistance_action(action: ActionType) -> bool:
    """Indica si la acción es de resistencia activa al cambio.

    Args:
        action: Tipo de acción.

    Returns:
        True si la acción resiste la reforma.
    """
    return action in RESISTANCE_ACTIONS
