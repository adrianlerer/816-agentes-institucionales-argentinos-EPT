"""
agents/firm.py — RegulatedFirmAgent: empresas reguladas.

50 empresas con bajo CRI (pro-reforma) pero capacidad de captura
regulatoria. Paradójicamente, sus intentos de CAPTURAR pueden
reforzar el CLI al crear incentivos perversos en el regulador.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class RegulatedFirmAgent(BaseLegalAgent):
    """Empresa regulada en el mercado laboral argentino.

    Las empresas tienen el CRI más bajo del sistema (0.20): son
    pro-reforma porque la flexibilización reduce sus costos laborales.
    Sin embargo, su capacidad de captura regulatoria es moderada (0.40)
    y sus recursos de litigio son limitados.

    Estrategia de decisión:
    - Pre-reforma: CUMPLIR (mínimo costo, conservar capital)
    - Post-reforma: CUMPLIR o CAPTURAR (capturar al regulador)
    - Si sancionada: LITIGAR (defensivo)
    - Si muy poca compliance: EVADIR

    Attributes:
        capture_capacity: Capacidad de captura regulatoria [0, 1].
        compliance_rate: Tasa de cumplimiento actual [0, 1].
    """

    def __init__(
        self,
        agent_id: str,
        cri: float,
        institutional_capital: float,
        capture_capacity: float,
        rng: random.Random,
    ):
        """Inicializa una empresa regulada.

        Args:
            agent_id: Identificador único.
            cri: Coeficiente de Resistencia Institucional (bajo: ~0.20).
            institutional_capital: Capital institucional.
            capture_capacity: Capacidad de captura del regulador [0, 1].
            rng: Generador aleatorio.
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="firm",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=[
                ActionType.CUMPLIR,
                ActionType.EVADIR,
                ActionType.LITIGAR,
                ActionType.CAPTURAR,
            ],
            rng=rng,
        )
        self.base_cost = 0.40
        self.capture_capacity = capture_capacity
        self.compliance_rate = 0.80  # tasa de cumplimiento inicial

    def decide_action(self, environment) -> ActionType:
        """Decide la estrategia de la empresa según el entorno regulatorio.

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        if environment.reform_active:
            # La reforma es favorable: CUMPLIR y tratar de acelerar
            if self.capture_capacity > 0.30 and self.rng.random() < self.capture_capacity * 0.5:
                return ActionType.CAPTURAR
            # Si hay mucha resistencia sindical, litigar para proteger intereses
            if environment.coalition_strength > 0.70 and self.rng.random() < 0.30:
                return ActionType.LITIGAR
            return ActionType.CUMPLIR
        else:
            # Pre-reforma: cumplir o evadir según la norma
            if self.rng.random() < 0.75:
                return ActionType.CUMPLIR
            return ActionType.EVADIR
