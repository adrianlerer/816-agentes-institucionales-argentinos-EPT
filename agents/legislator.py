"""
agents/legislator.py — LegislatorAgent: legisladores oficialistas y opositores.

130 oficialistas (pro-reforma, bajo CRI) + 127 opositores (anti-reforma, CRI medio).
La disciplina partidaria modula la autonomía individual.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class LegislatorAgent(BaseLegalAgent):
    """Legislador del Congreso de la Nación Argentina.

    Los legisladores tienen dos orientaciones posibles:
    - Oficialismo (pro-reforma): prefieren REFORMAR, discipline=0.80
    - Oposición (anti-reforma): prefieren IMPUGNAR_CN o COALICIONAR

    La disciplina partidaria reduce la probabilidad de desviarse de
    la posición del bloque, generando votaciones más predecibles.

    Attributes:
        party_discipline: Adhesión a la línea partidaria [0, 1].
        reform_preference: Preferencia por la reforma [0, 1].
            Alto = pro-reforma. Bajo = anti-reforma.
        is_oficialismo: True si es del bloque oficialista.
    """

    def __init__(
        self,
        agent_id: str,
        cri: float,
        institutional_capital: float,
        party_discipline: float,
        reform_preference: float,
        is_oficialismo: bool,
        rng: random.Random,
    ):
        """Inicializa un legislador.

        Args:
            agent_id: Identificador único.
            cri: Coeficiente de Resistencia Institucional.
            institutional_capital: Capital institucional.
            party_discipline: Disciplina partidaria [0, 1].
            reform_preference: Preferencia por la reforma [0, 1].
            is_oficialismo: True para oficialismo, False para oposición.
            rng: Generador aleatorio.
        """
        if is_oficialismo:
            actions = [ActionType.REFORMAR, ActionType.COALICIONAR]
        else:
            actions = [ActionType.IMPUGNAR_CN, ActionType.COALICIONAR]

        super().__init__(
            agent_id=agent_id,
            agent_type="legislator",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=actions,
            rng=rng,
        )
        self.base_cost = 0.35
        self.party_discipline = party_discipline
        self.reform_preference = reform_preference
        self.is_oficialismo = is_oficialismo

    def decide_action(self, environment) -> ActionType:
        """Decide la acción legislativa considerando disciplina partidaria.

        La disciplina partidaria determina qué tan frecuentemente el
        legislador sigue la línea del bloque vs. actúa individualmente.

        Oficialismo:
            - Alta disciplina + reforma activa → REFORMAR
            - Baja disciplina → puede COALICIONAR con oposición

        Oposición:
            - Alta disciplina + reforma activa → IMPUGNAR_CN
            - Baja disciplina → puede COALICIONAR o solo IMPUGNAR_CN

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        # ¿Sigue la línea del partido?
        follows_party = self.rng.random() < self.party_discipline

        if self.is_oficialismo:
            if environment.reform_active:
                if follows_party and self.reform_preference > 0.50:
                    return ActionType.REFORMAR
                else:
                    return ActionType.COALICIONAR
            else:
                return ActionType.COALICIONAR
        else:
            # Oposición
            if environment.reform_active:
                if follows_party:
                    return ActionType.IMPUGNAR_CN
                else:
                    return ActionType.COALICIONAR
            else:
                # Sin reforma activa: mantener posición
                if self.rng.random() < self.cri:
                    return ActionType.IMPUGNAR_CN
                return ActionType.COALICIONAR
