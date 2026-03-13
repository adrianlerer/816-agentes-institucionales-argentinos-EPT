"""
engine/hbu.py — Heteronomous Bayesian Updating.

Los agentes actualizan sus creencias sobre la validez de las normas
observando SANCIONES, no resultados sustantivos. Esto genera un
bucle de retroalimentación positivo en sistemas de alto CLI.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""


def hbu_update(
    prior_validity: float,
    sanction_observed: bool,
    p_sanction_given_valid: float = 0.80,
    p_sanction_given_invalid: float = 0.20,
) -> float:
    """Heteronomous Bayesian Updating.

    Los agentes actualizan su creencia sobre la validez de una norma
    basándose en si observaron una sanción (heteronomía) en lugar de
    razonar sobre el contenido sustantivo de la norma (autonomía).

    Este mecanismo genera un bucle patológico en sistemas de alto CLI:
    las sanciones refuerzan la creencia en la validez de la norma,
    lo cual incrementa el cumplimiento, lo cual reduce las sanciones
    por incumplimiento pero aumenta las sanciones a quienes intentan
    cambiarla — reforzando el lock-in.

    Fórmula:
        P(válida | sanción) = P(sanción | válida) × P(válida) / P(sanción)

    Args:
        prior_validity: Creencia previa sobre validez de la norma [0, 1].
        sanction_observed: True si se observó una sanción en esta ronda.
        p_sanction_given_valid: P(sanción | norma válida). Default 0.80.
            Alta porque las normas válidas se aplican con fuerza.
        p_sanction_given_invalid: P(sanción | norma inválida). Default 0.20.
            Baja porque las normas inválidas tienen menos enforcement.

    Returns:
        Posterior actualizado sobre validez [0, 1].

    Example:
        >>> # Agente observa sanción con prior 0.5
        >>> hbu_update(0.5, sanction_observed=True)
        0.8
        >>> # Agente NO observa sanción con prior 0.5
        >>> hbu_update(0.5, sanction_observed=False)
        0.2857142857142857
    """
    prior_validity = max(0.0, min(1.0, prior_validity))

    if sanction_observed:
        # P(sanción) = P(sanción|válida)·P(válida) + P(sanción|inválida)·P(inválida)
        p_sanction = (
            p_sanction_given_valid * prior_validity
            + p_sanction_given_invalid * (1.0 - prior_validity)
        )
        if p_sanction == 0.0:
            return prior_validity
        # Teorema de Bayes
        posterior = p_sanction_given_valid * prior_validity / p_sanction
    else:
        # P(no sanción) = P(¬s|válida)·P(válida) + P(¬s|inválida)·P(inválida)
        p_no_sanction = (
            (1.0 - p_sanction_given_valid) * prior_validity
            + (1.0 - p_sanction_given_invalid) * (1.0 - prior_validity)
        )
        if p_no_sanction == 0.0:
            return prior_validity
        posterior = (
            (1.0 - p_sanction_given_valid) * prior_validity / p_no_sanction
        )

    return max(0.0, min(1.0, posterior))


def hbu_batch_update(
    agents: list,
    sanctions_this_round: set,
) -> None:
    """Actualiza la creencia de validez de normas para todos los agentes.

    Itera sobre la lista de agentes. Aquellos que observaron o recibieron
    una sanción actualizan hacia mayor creencia en validez de la norma;
    los demás actualizan hacia menor creencia.

    Args:
        agents: Lista de objetos agente con atributo `norm_validity_belief`.
        sanctions_this_round: Conjunto de IDs de agentes sancionados.
    """
    for agent in agents:
        observed = agent.agent_id in sanctions_this_round
        agent.norm_validity_belief = hbu_update(
            prior_validity=agent.norm_validity_belief,
            sanction_observed=observed,
        )
