"""engine — Motor de simulación EPT.

Módulos:
    actions    — 9 ActionTypes + costos
    hbu        — Heteronomous Bayesian Updating
    resistance — CRI: costo asimétrico de abandono doctrinal
    metrics    — CLI, IHR, IEI, fitness
    environment — LegalEnvironment (estado global)
    simulation — Motor principal (10 pasos por ronda)
"""
from engine.actions import ActionType, ACTION_COSTS, get_action_cost
from engine.hbu import hbu_update
from engine.resistance import should_maintain_position
from engine.metrics import compute_cli, compute_doctrine_fitness
from engine.environment import LegalEnvironment

__all__ = [
    "ActionType",
    "ACTION_COSTS",
    "get_action_cost",
    "hbu_update",
    "should_maintain_position",
    "compute_cli",
    "compute_doctrine_fitness",
    "LegalEnvironment",
]
