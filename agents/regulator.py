"""
agents/regulator.py — RegulatorAgent: el regulador (MTSS u organismo equivalente).

1 agente regulador con vulnerabilidad a captura moderada.
Puede ser capturado por empresas (reduce su efectividad sancionadora)
o actuar autónomamente (refuerza norma vigente).

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base import BaseLegalAgent
from engine.actions import ActionType


class RegulatorAgent(BaseLegalAgent):
    """Regulador laboral (Ministerio de Trabajo o AFIP-laboral).

    El regulador tiene CRI moderado (0.40) y es vulnerable a captura
    por las empresas. Cuando es capturado, reduce su frecuencia de
    sanciones, lo cual vía HBU reduce la percepción de validez de las
    normas por parte de los ciudadanos.

    Attributes:
        capture_vulnerability: Vulnerabilidad a la captura [0, 1].
        is_captured: True si el regulador está actualmente capturado.
        capture_rounds: Rondas restantes de captura.
    """

    def __init__(
        self,
        agent_id: str,
        cri: float,
        institutional_capital: float,
        capture_vulnerability: float,
        rng: random.Random,
    ):
        """Inicializa el regulador.

        Args:
            agent_id: Identificador único.
            cri: Coeficiente de Resistencia Institucional (~0.40).
            institutional_capital: Capital institucional (~0.60).
            capture_vulnerability: Vulnerabilidad a captura [0, 1].
            rng: Generador aleatorio.
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="regulator",
            cri=cri,
            institutional_capital=institutional_capital,
            available_actions=[ActionType.SANCIONAR],
            rng=rng,
        )
        self.base_cost = 0.30
        self.capture_vulnerability = capture_vulnerability
        self.is_captured = False
        self.capture_rounds = 0

    def receive_capture_attempt(self, capture_capacity: float) -> bool:
        """Procesa un intento de captura por parte de una empresa.

        Args:
            capture_capacity: Capacidad de captura de la empresa [0, 1].

        Returns:
            True si la captura fue exitosa.
        """
        # Probabilidad de captura: producto de vulnerabilidad y capacidad
        p_capture = self.capture_vulnerability * capture_capacity
        if self.rng.random() < p_capture:
            self.is_captured = True
            self.capture_rounds = self.rng.randint(3, 8)  # dura 3-8 rondas
            return True
        return False

    def tick_capture(self) -> None:
        """Decrementa el contador de captura al inicio de cada ronda."""
        if self.is_captured:
            self.capture_rounds -= 1
            if self.capture_rounds <= 0:
                self.is_captured = False

    def decide_action(self, environment) -> ActionType:
        """Decide si sancionar según si está capturado.

        Un regulador capturado sanciona con mucha menos frecuencia
        (reducción del 70%), lo que vía HBU reduce la percepción de
        validez de las normas.

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType.SANCIONAR siempre (es la única acción disponible),
            pero el efecto es nulo si está capturado.
        """
        # Si capturado: puede "decidir no sancionar" (sin efecto real)
        # El motor omite el efecto si is_captured=True
        return ActionType.SANCIONAR
