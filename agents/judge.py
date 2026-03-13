"""
agents/judge.py — JudgeAgent: jueces de la CSJN.

5 jueces con alto CRI y capital institucional máximo.
Son el principal veto player del sistema.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class JudgeAgent(BaseLegalAgent):
    """Juez de la Corte Suprema de Justicia de la Nación Argentina.

    Los jueces CSJN tienen el mayor CRI del sistema (0.78) y el mayor
    capital institucional (0.90). Son veto players constitucionales:
    pueden revisar, suspender o revertir leyes.

    Su estrategia de decisión privilegia la defensa de la doctrina
    consolidada por sobre la reforma. Cuando la reforma activa amenaza
    la doctrina, prefieren IMPUGNAR_CN o REVERSAR. Si ya hay litigio
    en curso, SANCIONAR para reforzar la norma vigente.

    Attributes:
        doctrinal_conservatism: Sesgo hacia la doctrina preexistente [0, 1].
        review_threshold: Umbral mínimo de doctrine_fitness para no revisar.
    """

    def __init__(
        self,
        agent_id: str,
        cri: float,
        institutional_capital: float,
        rng: random.Random,
    ):
        """Inicializa un juez CSJN.

        Args:
            agent_id: Identificador único (ej: 'judge_0').
            cri: Coeficiente de Resistencia Institucional (default 0.78).
            institutional_capital: Capital institucional (default 0.90).
            rng: Generador aleatorio con seed controlada.
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="judge",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=[
                ActionType.SANCIONAR,
                ActionType.REVERSAR,
                ActionType.IMPUGNAR_CN,
            ],
            rng=rng,
        )
        self.base_cost = 0.25
        self.doctrinal_conservatism = 0.85
        self.review_threshold = 0.60  # si fitness < 0.60, inicia revisión

    def decide_action(self, environment) -> ActionType:
        """Decide la acción judicial según el estado institucional.

        Lógica de decisión:
        1. Si reforma activa y doctrine_fitness bajo → REVERSAR (bloqueo fuerte)
        2. Si reforma activa y hay litigio previo → IMPUGNAR_CN
        3. Si reforma activa → SANCIONAR (refuerza norma vigente)
        4. Si no hay reforma → SANCIONAR (mantenimiento rutinario)

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        if environment.reform_active:
            if environment.doctrine_fitness < self.review_threshold:
                # Doctrina amenazada: revertir activamente
                return ActionType.REVERSAR
            # Verificar si hay litigio en curso (coal o litigio de sindicatos)
            recent_union = environment.get_recent_actions("union", n=5)
            litigating = any(
                r["action"] == ActionType.LITIGAR for r in recent_union
            )
            if litigating:
                return ActionType.IMPUGNAR_CN
            return ActionType.SANCIONAR
        else:
            # Sin reforma: mantenimiento doctrinario rutinario
            return ActionType.SANCIONAR
