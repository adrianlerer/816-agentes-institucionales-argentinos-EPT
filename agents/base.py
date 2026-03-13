"""
agents/base.py — BaseLegalAgent: clase base para todos los agentes.

Todos los agentes institucionales heredan de esta clase.
Contiene CRI, HBU, doctrinal_memory y la interfaz decide_action.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from engine.actions import ActionType


class BaseLegalAgent:
    """Agente institucional base con CRI, HBU y memoria doctrinal.

    Attributes:
        agent_id: Identificador único del agente.
        agent_type: Tipo de agente (string para logs).
        cri: Coefficient of Resistance Institutional [0, 1].
            Alto = muy resistente al cambio doctrinal.
        institutional_capital: Capital institucional acumulado [0, 1].
            Representa poder, legitimidad y recursos.
        base_cost: Costo base de acciones (fracción del capital).
        norm_validity_belief: Creencia bayesiana sobre validez de normas [0, 1].
        doctrinal_memory: Historial de posiciones doctrinales.
        n_supporters: Número de agentes con la misma posición doctrinal.
        available_actions: Lista de ActionType disponibles para este agente.
        rng: Generador de números aleatorios (seed controlada externamente).
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        cri: float,
        institutional_capital: float,
        available_actions: list[ActionType],
        rng: random.Random,
    ):
        """Inicializa el agente base.

        Args:
            agent_id: Identificador único (ej: 'judge_0', 'union_cgt').
            agent_type: Tipo de agente para logs.
            cri: Coeficiente de Resistencia Institucional [0, 1].
            institutional_capital: Capital institucional [0, 1].
            available_actions: Acciones que puede realizar este agente.
            rng: Generador aleatorio con seed controlada.
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.cri = max(0.0, min(1.0, cri))
        self.institutional_capital = max(0.0, min(1.0, institutional_capital))
        self.base_cost = 0.30  # costo base por defecto
        self.norm_validity_belief = 0.70  # prior inicial: normas vigentes son válidas
        self.doctrinal_memory: list[str] = []  # historial de posiciones
        self.n_supporters: int = 0  # actualizado por el motor en cada ronda
        self.available_actions = available_actions
        self.rng = rng
        self.fitness_history: list[float] = []

    def decide_action(self, environment) -> ActionType:
        """Decide qué acción tomar en la ronda actual.

        Implementación base: selecciona la acción con menor costo
        ponderada por la creencia de validez de norma y el CRI.

        Las subclases deben sobreescribir este método con lógica
        específica del tipo de agente.

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        from engine.actions import ACTION_COSTS

        if not self.available_actions:
            return ActionType.CUMPLIR

        # Ponderación: agentes con alto CRI prefieren acciones de resistencia
        # cuando la reforma está activa
        if environment.reform_active and self.cri > 0.50:
            from engine.actions import RESISTANCE_ACTIONS
            resist = [a for a in self.available_actions if a in RESISTANCE_ACTIONS]
            if resist:
                # Elegir acción de resistencia de menor costo
                return min(resist, key=lambda a: ACTION_COSTS[a])

        # Por defecto: acción de menor costo disponible
        return min(self.available_actions, key=lambda a: ACTION_COSTS[a])

    def update_belief(self, sanction_observed: bool) -> None:
        """Actualiza la creencia sobre validez de normas (HBU).

        Args:
            sanction_observed: True si el agente observó/recibió una sanción.
        """
        from engine.hbu import hbu_update
        self.norm_validity_belief = hbu_update(
            prior_validity=self.norm_validity_belief,
            sanction_observed=sanction_observed,
        )

    def record_position(self, position: str) -> None:
        """Registra una posición doctrinal en la memoria del agente.

        Args:
            position: Descripción de la posición doctrinal adoptada.
        """
        self.doctrinal_memory.append(position)
        # Mantener solo las últimas 20 posiciones
        if len(self.doctrinal_memory) > 20:
            self.doctrinal_memory = self.doctrinal_memory[-20:]

    def get_resistance_probability(self, doctrine_fitness: float) -> float:
        """Calcula la probabilidad de resistir el cambio dado el fitness doctrinal.

        Combina CRI con la evaluación del costo asimétrico para producir
        una probabilidad continua de resistencia.

        Args:
            doctrine_fitness: Fitness de la doctrina actual [0, 1].

        Returns:
            Probabilidad de resistencia [0, 1].
        """
        from engine.resistance import should_maintain_position
        # Actualizar n_supporters desde la memoria
        base_resist = should_maintain_position(self, doctrine_fitness)
        # Agregar componente estocástico basado en CRI
        prob = self.cri * 0.7 + (0.3 if base_resist else 0.0)
        return max(0.0, min(1.0, prob))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.agent_id}, "
            f"cri={self.cri:.2f}, "
            f"ic={self.institutional_capital:.2f})"
        )
