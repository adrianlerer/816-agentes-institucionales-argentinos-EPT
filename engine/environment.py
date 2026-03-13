"""
engine/environment.py — LegalEnvironment: estado del sistema institucional.

Contiene el estado global de normas, precedentes y coaliciones.
Es el "mundo" en el que los agentes interactúan.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

from engine.actions import ActionType, get_cli_effect


class LegalEnvironment:
    """Entorno jurídico-institucional compartido por todos los agentes.

    Mantiene el estado global de:
    - Normas vigentes (doctrina base)
    - Precedentes judiciales acumulados
    - Estado de coaliciones activas
    - Fase de la reforma (pre/post introducción)
    - Historial de CLI por ronda

    Attributes:
        round_number: Ronda actual de simulación.
        reform_active: True si la reforma fue introducida.
        reform_trigger_round: Ronda en que se introduce la reforma.
        doctrine_fitness: Fitness de la doctrina vigente [0, 1].
        precedent_strength: Fuerza acumulada de precedentes [0, 1].
        coalition_active: True si hay coalición anti-reforma activa.
        cli_history: Lista de valores CLI por ronda.
        reform_attempts: Total de intentos de reforma.
        reform_blocked: Intentos de reforma bloqueados.
        sanctions_this_round: IDs de agentes sancionados en la ronda.
        action_log: Registro histórico de acciones.
    """

    def __init__(self, config: dict, rng=None):
        """Inicializa el entorno con la configuración del escenario.

        Args:
            config: Diccionario del escenario (cargado desde argentina.yaml).
            rng: Generador aleatorio opcional (para reproduciblidad en bloqueo estocástico).
        """
        import random as _random
        self._rng = rng if rng is not None else _random.Random(0)
        self.round_number: int = 0
        self.reform_active: bool = False
        self.reform_trigger_round: int = config["scenario"]["reform_trigger_round"]
        self.cli_weights: dict = config["cli_weights"]

        # Estado doctrinal inicial (pre-reforma: doctrina consolidada)
        self.doctrine_fitness: float = 0.85
        self.precedent_strength: float = 0.80
        self.informal_norm_strength: float = 0.88
        self.amendment_difficulty: float = 0.82

        # Estado de coaliciones
        self.coalition_active: bool = False
        self.coalition_strength: float = 0.0

        # Registro de resultados
        self.cli_history: list[float] = []
        self.reform_attempts: int = 0
        self.reform_blocked: int = 0
        self.sanctions_this_round: set[str] = set()
        self.action_log: list[dict] = []

        # Veto player score (computado en cada ronda)
        # Cap en 0.92 para evitar saturación: CLI ~0.923 target
        self.veto_player_score: float = 0.75
        self._veto_cap: float = 0.92

        # Judicial review score — cap en 0.94
        self.judicial_review_score: float = 0.80
        self._jr_cap: float = 0.94

        # Amendment difficulty — cap en 0.93
        self._ad_cap: float = 0.93

        # Informal norms — cap en 0.94
        self._in_cap: float = 0.94

    def start_round(self, round_number: int) -> None:
        """Inicia una nueva ronda, disparando la reforma si corresponde.

        Args:
            round_number: Número de la ronda actual.
        """
        self.round_number = round_number
        self.sanctions_this_round = set()

        # Activar reforma en la ronda trigger
        if round_number == self.reform_trigger_round and not self.reform_active:
            self.reform_active = True
            # La reforma reduce temporalmente el fitness doctrinal
            self.doctrine_fitness = max(0.40, self.doctrine_fitness - 0.25)
            self.amendment_difficulty = max(0.50, self.amendment_difficulty - 0.15)

    def apply_action(self, agent_id: str, agent_type: str, action: ActionType) -> None:
        """Registra una acción y actualiza el estado del entorno.

        Args:
            agent_id: ID único del agente.
            agent_type: Tipo de agente ('judge', 'union', etc.).
            action: Tipo de acción realizada.
        """
        # Registrar en log
        self.action_log.append({
            "round": self.round_number,
            "agent_id": agent_id,
            "agent_type": agent_type,
            "action": action,
        })

        # Actualizar estado según la acción
        cli_delta = get_cli_effect(action)

        if action == ActionType.COALICIONAR:
            self.coalition_active = True
            self.coalition_strength = min(0.98, self.coalition_strength + 0.005)
            self.veto_player_score = min(self._veto_cap, self.veto_player_score + 0.002)

        elif action == ActionType.LITIGAR:
            self.judicial_review_score = min(self._jr_cap, self.judicial_review_score + 0.002)
            # LITIGAR no cuenta como intento de reforma — es respuesta a la reforma

        elif action == ActionType.IMPUGNAR_CN:
            self.judicial_review_score = min(self._jr_cap, self.judicial_review_score + 0.003)
            self.amendment_difficulty = min(self._ad_cap, self.amendment_difficulty + 0.002)
            # IMPUGNAR_CN no cuenta como intento — es mecanismo de bloqueo

        elif action == ActionType.REVERSAR:
            # Juez revierte reforma: bloqueo efectivo
            if self.reform_active:
                self.doctrine_fitness = min(1.0, self.doctrine_fitness + 0.004)

        elif action == ActionType.SANCIONAR:
            # Sanción: refuerza percepción de validez de norma
            self.sanctions_this_round.add(agent_id)
            self.doctrine_fitness = min(1.0, self.doctrine_fitness + 0.001)

        elif action == ActionType.REFORMAR:
            # Intento de reforma: único tipo que cuenta como attempt/block
            self.reform_attempts += 1
            # La reforma es bloqueada estocásticamente según el poder de resistencia.
            # Resistencia = promedio ponderado de veto, judicial y coalición.
            # Con Argentina (resistance ≈0.937): ~93.8% de los intentos se bloquean.
            resistance = (
                0.40 * self.veto_player_score
                + 0.35 * self.judicial_review_score
                + 0.25 * self.coalition_strength
            )
            # Bloqueo estocástico: random() < resistance → bloqueado
            if self._rng.random() < resistance:
                self.reform_blocked += 1
            else:
                self.doctrine_fitness = max(0.30, self.doctrine_fitness - 0.002)

        elif action == ActionType.EVADIR:
            self.informal_norm_strength = max(0.0, self.informal_norm_strength - 0.001)

        elif action == ActionType.CAPTURAR:
            # Captura regulatoria: debilita veto players
            self.veto_player_score = max(0.0, self.veto_player_score - 0.002)

        # Pequeño ajuste global basado en efecto CLI (amortiguado)
        self.judicial_review_score = max(
            0.0, min(self._jr_cap, self.judicial_review_score + cli_delta * 0.05)
        )
        self.informal_norm_strength = max(
            0.0, min(self._in_cap, self.informal_norm_strength + cli_delta * 0.03)
        )

    def compute_current_cli(self) -> float:
        """Calcula el CLI de la ronda actual.

        Combina los cuatro componentes ponderados con los pesos de
        la configuración del escenario.

        Returns:
            CLI actual [0, 1].
        """
        from engine.metrics import compute_cli
        cli = compute_cli(
            veto_player_score=self.veto_player_score,
            judicial_review_score=self.judicial_review_score,
            amendment_difficulty=self.amendment_difficulty,
            informal_norms_score=self.informal_norm_strength,
            weights=self.cli_weights,
        )
        self.cli_history.append(cli)
        return cli

    def get_block_rate(self) -> float:
        """Calcula la tasa de bloqueo de reformas.

        Returns:
            Proporción de intentos de reforma bloqueados [0, 1].
        """
        if self.reform_attempts == 0:
            return 0.0
        return self.reform_blocked / self.reform_attempts

    def get_recent_actions(self, agent_type: str, n: int = 10) -> list:
        """Devuelve las N acciones más recientes de un tipo de agente.

        Args:
            agent_type: Tipo de agente a filtrar.
            n: Número de acciones a devolver.

        Returns:
            Lista de registros de acciones (más recientes primero).
        """
        filtered = [
            r for r in reversed(self.action_log)
            if r["agent_type"] == agent_type
        ]
        return filtered[:n]
