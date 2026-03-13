"""
engine/resistance.py — Modelo CRI: Coefficient of Resistance.

Implementa el costo asimétrico de abandonar posiciones doctrinales
consolidadas. Cuanto mayor el capital institucional y la cantidad de
seguidores, más costoso es abandonar una posición, independientemente
de su fitness doctrinal.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""


def compute_abandon_cost(
    base_cost: float,
    institutional_capital: float,
    n_supporters: int,
) -> float:
    """Calcula el costo de abandonar una posición doctrinal.

    El costo de abandono escala con el capital institucional acumulado
    y con la cantidad de seguidores: cuanto más arraigada la posición,
    más costoso renunciar a ella (path dependence institucional).

    Fórmula:
        cost_abandon = base_cost × institutional_capital × (1 + n_supporters)

    Args:
        base_cost: Costo base de la acción de abandono [0, 1].
        institutional_capital: Capital institucional del agente [0, 1].
        n_supporters: Número de agentes que sostienen la misma posición.

    Returns:
        Costo de abandono (puede ser > 1 con muchos seguidores).
    """
    return base_cost * institutional_capital * (1 + n_supporters)


def compute_maintain_cost(
    base_cost: float,
    doctrine_fitness: float,
) -> float:
    """Calcula el costo de mantener una posición doctrinal.

    Una doctrina de bajo fitness (poco adoptada, frecuentemente
    impugnada) es costosa de mantener. Una de alto fitness es
    casi gratuita de mantener.

    Fórmula:
        cost_maintain = base_cost × (1 - doctrine_fitness)

    Args:
        base_cost: Costo base [0, 1].
        doctrine_fitness: Fitness de la doctrina en el entorno [0, 1].
            fitness = tasa_adopción / (tasa_adopción + tasa_litigio + ε)

    Returns:
        Costo de mantenimiento [0, 1].
    """
    return base_cost * (1.0 - doctrine_fitness)


def should_maintain_position(
    agent,
    doctrine_fitness: float,
) -> bool:
    """Decisión CRI: mantener o abandonar posición doctrinal.

    El agente mantiene su posición si el costo de abandonarla supera
    el costo ajustado de mantenerla (donde el ajuste incorpora el CRI
    como umbral de resistencia al cambio).

    Condición de mantenimiento:
        cost_abandon > cost_maintain × (1 + agent.cri)

    Cuando CRI es alto, el denominador efectivo sube, haciendo que
    el agente mantenga su posición incluso si doctrine_fitness es bajo.

    Args:
        agent: Agente con atributos `base_cost`, `institutional_capital`,
               `n_supporters` y `cri`.
        doctrine_fitness: Fitness de la doctrina actual [0, 1].

    Returns:
        True si el agente MANTIENE su posición (resiste el cambio).
        False si el agente ABANDONA (acepta el cambio).

    Example:
        >>> class MockAgent:
        ...     base_cost = 0.3
        ...     institutional_capital = 0.9
        ...     n_supporters = 4
        ...     cri = 0.78
        >>> should_maintain_position(MockAgent(), doctrine_fitness=0.3)
        True
    """
    cost_abandon = compute_abandon_cost(
        agent.base_cost,
        agent.institutional_capital,
        agent.n_supporters,
    )
    cost_maintain = compute_maintain_cost(
        agent.base_cost,
        doctrine_fitness,
    )
    # El CRI actúa como multiplicador del umbral: más CRI = más resistencia
    return cost_abandon > cost_maintain * (1.0 + agent.cri)


def compute_resistance_score(
    agents: list,
    doctrine_fitness: float,
) -> float:
    """Calcula la puntuación de resistencia agregada de un grupo de agentes.

    Proporción de agentes del grupo que mantendría su posición
    doctrinal dado el fitness actual.

    Args:
        agents: Lista de agentes a evaluar.
        doctrine_fitness: Fitness de la doctrina vigente [0, 1].

    Returns:
        Fracción de agentes que resisten [0, 1].
    """
    if not agents:
        return 0.0
    maintainers = sum(
        1 for a in agents if should_maintain_position(a, doctrine_fitness)
    )
    return maintainers / len(agents)
