"""
agents/union.py — UnionAgent: CGT, CTA y sindicatos sectoriales.

Los sindicatos son los agentes con mayor capacidad de coalición.
Su estrategia dominante post-reforma es COALICIONAR + LITIGAR,
lo que produce el 65% de estrategia COAL+LIT observado en la simulación.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class UnionAgent(BaseLegalAgent):
    """Sindicato (CGT, CTA o sectorial).

    Los sindicatos combinan capacidad de huelga (strike_capacity),
    litigio judicial (legal_resources) y formación de coaliciones
    (coalition_capacity). Son los actores con CRI más alto del sistema
    después de los jueces.

    Estrategia de decisión:
    - Pre-reforma: COALICIONAR preventivo
    - Post-reforma: COALICIONAR si capacidad alta, sino LITIGAR
    - Si capital bajo: EVADIR para conservar recursos

    Attributes:
        union_name: Nombre de la confederación ('CGT', 'CTA', 'Sectorial').
        coalition_capacity: Capacidad de formar coaliciones [0, 1].
        strike_capacity: Capacidad de huelga y movilización [0, 1].
        legal_resources: Recursos para litigio judicial [0, 1].
    """

    def __init__(
        self,
        agent_id: str,
        union_name: str,
        cri: float,
        institutional_capital: float,
        coalition_capacity: float,
        strike_capacity: float,
        legal_resources: float,
        available_actions: list[ActionType],
        rng: random.Random,
    ):
        """Inicializa un sindicato.

        Args:
            agent_id: Identificador único.
            union_name: Nombre ('CGT', 'CTA', 'Sectorial').
            cri: Coeficiente de Resistencia Institucional.
            institutional_capital: Capital institucional.
            coalition_capacity: Capacidad de coalición [0, 1].
            strike_capacity: Capacidad de huelga [0, 1].
            legal_resources: Recursos de litigio [0, 1].
            available_actions: Acciones disponibles para este sindicato.
            rng: Generador aleatorio.
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="union",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=available_actions,
            rng=rng,
        )
        self.base_cost = 0.20
        self.union_name = union_name
        self.coalition_capacity = coalition_capacity
        self.strike_capacity = strike_capacity
        self.legal_resources = legal_resources

    def decide_action(self, environment) -> ActionType:
        """Decide la estrategia sindical según el estado institucional.

        Lógica de decisión calibrada para producir COAL+LIT ~65%:
        - CGT (coalition=0.95): 55% COAL, 20% LITIGAR, 25% EVADIR
        - CTA (coalition=0.85): 50% COAL, 25% LITIGAR, 25% EVADIR
        - Sectorial (coalition=0.70): 40% COAL, 25% LITIGAR, 35% EVADIR

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        if environment.reform_active:
            rand = self.rng.random()

            # Probabilidades calibradas por capacidad del sindicato
            # Para producir COAL+LIT ~65%: el resto es EVADIR o CUMPLIR
            coal_prob = self.coalition_capacity * 0.60   # CGT=0.57, CTA=0.51, Sec=0.42
            lit_prob = self.legal_resources * 0.15       # CGT=0.13, CTA=0.11, Sec=0.09
            # evadir_prob = 1 - coal_prob - lit_prob

            if rand < coal_prob and ActionType.COALICIONAR in self.available_actions:
                return ActionType.COALICIONAR
            elif rand < coal_prob + lit_prob and ActionType.LITIGAR in self.available_actions:
                return ActionType.LITIGAR
            elif ActionType.EVADIR in self.available_actions:
                return ActionType.EVADIR
            elif ActionType.LITIGAR in self.available_actions:
                return ActionType.LITIGAR
            else:
                return ActionType.COALICIONAR

        else:
            # Pre-reforma: mayormente COALICIONAR preventivo
            rand = self.rng.random()
            coal_prob_pre = self.coalition_capacity * 0.65
            if rand < coal_prob_pre and ActionType.COALICIONAR in self.available_actions:
                return ActionType.COALICIONAR
            elif ActionType.EVADIR in self.available_actions:
                return ActionType.EVADIR
            return super().decide_action(environment)
