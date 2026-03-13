"""
engine/metrics.py — CLI, IHR, IEI y métricas de fitness.

Constitutional Lock-in Index (CLI): mide la rigidez estructural
del sistema institucional. Es un índice compuesto ponderado.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import math


def compute_cli(
    veto_player_score: float,
    judicial_review_score: float,
    amendment_difficulty: float,
    informal_norms_score: float,
    weights: dict | None = None,
) -> float:
    """Calcula el Constitutional Lock-in Index (CLI).

    El CLI es un índice compuesto que mide cuán difícil es modificar
    el statu quo institucional. Se compone de cuatro dimensiones
    ponderadas fijadas por calibración con datos históricos argentinos.

    Fórmula:
        CLI = w1·VP + w2·JR + w3·AD + w4·IN

    Donde:
        VP = veto player score (poder de bloqueo de actores clave)
        JR = judicial review score (activismo del poder judicial)
        AD = amendment difficulty (rigidez formal de la norma)
        IN = informal norms score (arraigo de normas informales)

    Pesos por defecto (calibrados para Argentina):
        w1=0.30, w2=0.25, w3=0.25, w4=0.20

    Args:
        veto_player_score: Poder agregado de veto players [0, 1].
        judicial_review_score: Intensidad del control judicial [0, 1].
        amendment_difficulty: Rigidez formal para modificar normas [0, 1].
        informal_norms_score: Arraigo de normas informales [0, 1].
        weights: Diccionario con pesos {'veto_players': ..., 'judicial_review': ...,
                 'amendment_difficulty': ..., 'informal_norms': ...}.
                 Si None, usa los pesos calibrados para Argentina.

    Returns:
        CLI en [0, 1]. Valores > 0.80 indican lock-in fuerte.

    Example:
        >>> compute_cli(0.90, 0.85, 0.80, 0.85)
        0.8575
    """
    if weights is None:
        weights = {
            "veto_players": 0.30,
            "judicial_review": 0.25,
            "amendment_difficulty": 0.25,
            "informal_norms": 0.20,
        }

    cli = (
        weights["veto_players"] * veto_player_score
        + weights["judicial_review"] * judicial_review_score
        + weights["amendment_difficulty"] * amendment_difficulty
        + weights["informal_norms"] * informal_norms_score
    )
    return max(0.0, min(1.0, cli))


def compute_doctrine_fitness(
    adoption_rate: float,
    litigation_rate: float,
    epsilon: float = 1e-6,
) -> float:
    """Calcula el fitness de una doctrina jurídica (EPT).

    En el marco de Extended Phenotype Theory, el fitness de una norma
    se define como su tasa de adopción relativa a su tasa de litigio:
    una norma muy adoptada y poco impugnada tiene fitness alto.

    Fórmula:
        fitness = adoption / (adoption + litigation + ε)

    Args:
        adoption_rate: Tasa de adopción de la norma [0, 1].
        litigation_rate: Tasa de litigio contra la norma [0, 1].
        epsilon: Constante de estabilidad numérica.

    Returns:
        Fitness de la doctrina [0, 1].
    """
    return adoption_rate / (adoption_rate + litigation_rate + epsilon)


def compute_ihr(
    n_blocked: int,
    n_total: int,
) -> float:
    """Calcula el Institutional Hardening Rate (IHR).

    Proporción de intentos de reforma que fueron bloqueados por el
    sistema institucional. Un IHR > 0.70 indica sistema muy rígido.

    Args:
        n_blocked: Número de intentos de reforma bloqueados.
        n_total: Número total de intentos de reforma.

    Returns:
        IHR en [0, 1].
    """
    if n_total == 0:
        return 0.0
    return n_blocked / n_total


def compute_iei(
    cli_values: list[float],
) -> float:
    """Calcula el Institutional Entropy Index (IEI).

    Mide la variabilidad del CLI a lo largo de la simulación.
    Bajo IEI indica atractor fuerte (equilibrio estable).

    Usa entropía de Shannon normalizada sobre la distribución del CLI.

    Args:
        cli_values: Serie temporal de valores CLI.

    Returns:
        IEI en [0, 1]. Bajo = atractor fuerte. Alto = sistema inestable.
    """
    if len(cli_values) < 2:
        return 0.0

    # Histograma de 10 bins sobre [0, 1]
    n_bins = 10
    counts = [0] * n_bins
    for v in cli_values:
        idx = min(int(v * n_bins), n_bins - 1)
        counts[idx] += 1

    total = sum(counts)
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * math.log2(p)

    # Normalizar por entropía máxima (log2(n_bins))
    max_entropy = math.log2(n_bins)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def compute_union_coal_lit_rate(action_log: list[dict]) -> float:
    """Calcula la tasa de estrategia COALICIONAR+LITIGAR en sindicatos.

    Proporción de acciones sindicales que corresponden a las estrategias
    de coalición o litigio. Un valor > 0.50 indica predominio de la
    estrategia de resistencia organizada.

    Args:
        action_log: Lista de registros {'agent_type': str, 'action': ActionType}.

    Returns:
        Tasa COAL+LIT en acciones sindicales [0, 1].
    """
    from engine.actions import ActionType

    union_actions = [
        r for r in action_log if r.get("agent_type") == "union"
    ]
    if not union_actions:
        return 0.0

    coal_lit = sum(
        1
        for r in union_actions
        if r["action"] in (ActionType.COALICIONAR, ActionType.LITIGAR)
    )
    return coal_lit / len(union_actions)
