"""
agents/citizen.py — CitizenAgent: ciudadanos (500 agentes).

500 ciudadanos con bajo CRI y mínimo capital institucional.
Son los actores más atomizados del sistema. Su comportamiento
individual tiene poco efecto en el CLI pero en conjunto generan
la base de la norma informal.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class CitizenAgent(BaseLegalAgent):
    """Ciudadano trabajador en el sistema laboral argentino.

    Los ciudadanos tienen el menor CRI (0.15) y el menor capital
    institucional (0.10). Solo pueden CUMPLIR o EVADIR. Su tasa
    de evasión aumenta cuando observan que la norma es impugnada
    o tiene bajo fitness (efecto HBU).

    Attributes:
        coalition_capacity: Capacidad de organizarse colectivamente [0, 1].
        evasion_threshold: Umbral de fitness doctrinal para empezar a evadir.
    """

    def __init__(
        self,
        agent_id: str,
        cri: float,
        institutional_capital: float,
        coalition_capacity: float,
        rng: random.Random,
    ):
        """Inicializa un ciudadano.

        Args:
            agent_id: Identificador único.
            cri: Coeficiente de Resistencia Institucional (bajo: ~0.15).
            institutional_capital: Capital institucional (bajo: ~0.10).
            coalition_capacity: Capacidad de coalición (baja: ~0.20).
            rng: Generador aleatorio.
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="citizen",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=[ActionType.CUMPLIR, ActionType.EVADIR],
            rng=rng,
        )
        self.base_cost = 0.10
        self.coalition_capacity = coalition_capacity
        self.evasion_threshold = 0.40

    def decide_action(self, environment) -> ActionType:
        """Decide si cumplir o evadir según la validez percibida de la norma.

        Los ciudadanos usan HBU: si la norma tiene bajo fitness percibido
        (muchas sanciones a quienes la acatan), aumentan su evasión.

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType.CUMPLIR o ActionType.EVADIR.
        """
        # Con alta creencia de validez → cumplir
        if self.norm_validity_belief > 0.60:
            return ActionType.CUMPLIR

        # Bajo fitness doctrinal → más evasión
        if environment.doctrine_fitness < self.evasion_threshold:
            if self.rng.random() < (1.0 - environment.doctrine_fitness):
                return ActionType.EVADIR

        # Por defecto: cumplir (mínimo costo)
        return ActionType.CUMPLIR
