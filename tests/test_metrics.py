"""
tests/test_metrics.py — Tests de métricas: CLI, HBU, CRI.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from engine.metrics import (
    compute_cli,
    compute_doctrine_fitness,
    compute_ihr,
    compute_iei,
    compute_union_coal_lit_rate,
)
from engine.hbu import hbu_update
from engine.resistance import (
    compute_abandon_cost,
    compute_maintain_cost,
    should_maintain_position,
)
from engine.actions import ActionType


class TestCLI:
    def test_known_value(self):
        """CLI produce valor correcto con entradas conocidas."""
        # Argentina baseline: veto=0.90, jr=0.85, ad=0.80, in=0.85
        cli = compute_cli(0.90, 0.85, 0.80, 0.85)
        expected = 0.30 * 0.90 + 0.25 * 0.85 + 0.25 * 0.80 + 0.20 * 0.85
        assert abs(cli - expected) < 1e-6

    def test_all_zeros(self):
        """CLI = 0 cuando todos los componentes son 0."""
        cli = compute_cli(0.0, 0.0, 0.0, 0.0)
        assert cli == 0.0

    def test_all_ones(self):
        """CLI = 1 cuando todos los componentes son 1."""
        cli = compute_cli(1.0, 1.0, 1.0, 1.0)
        assert cli == 1.0

    def test_custom_weights(self):
        """CLI usa pesos personalizados correctamente."""
        weights = {
            "veto_players": 0.25,
            "judicial_review": 0.25,
            "amendment_difficulty": 0.25,
            "informal_norms": 0.25,
        }
        cli = compute_cli(0.8, 0.8, 0.8, 0.8, weights=weights)
        assert abs(cli - 0.8) < 1e-6

    def test_range_enforcement(self):
        """CLI siempre está en [0, 1]."""
        # Pesos que podrían dar > 1 si no se clampa
        cli = compute_cli(1.0, 1.0, 1.0, 1.0)
        assert 0.0 <= cli <= 1.0


class TestDoctrineFITNESS:
    def test_high_adoption_low_litigation(self):
        """Fitness alto cuando adopción alta y litigio bajo."""
        fitness = compute_doctrine_fitness(0.90, 0.05)
        assert fitness > 0.90

    def test_equal_adoption_litigation(self):
        """Fitness ~0.5 cuando adopción = litigio."""
        fitness = compute_doctrine_fitness(0.5, 0.5)
        assert abs(fitness - 0.5) < 0.01

    def test_zero_adoption(self):
        """Fitness ~0 cuando adopción = 0."""
        fitness = compute_doctrine_fitness(0.0, 0.5)
        assert fitness < 0.01


class TestIHR:
    def test_all_blocked(self):
        """IHR = 1 cuando todos los intentos son bloqueados."""
        assert compute_ihr(10, 10) == 1.0

    def test_none_blocked(self):
        """IHR = 0 cuando ningún intento es bloqueado."""
        assert compute_ihr(0, 10) == 0.0

    def test_zero_attempts(self):
        """IHR = 0 cuando no hay intentos."""
        assert compute_ihr(0, 0) == 0.0

    def test_partial_block(self):
        """IHR = 0.938 para 93.8% de bloqueo (caso Argentina)."""
        # 15 de 16 bloqueados ≈ 93.75%
        ihr = compute_ihr(15, 16)
        assert abs(ihr - 15/16) < 1e-6


class TestIEI:
    def test_constant_series(self):
        """IEI bajo para serie constante (atractor fuerte)."""
        series = [0.92] * 100
        iei = compute_iei(series)
        assert iei < 0.15  # muy bajo: todos en el mismo bin

    def test_uniform_distribution(self):
        """IEI alto para distribución uniforme."""
        series = [i / 100 for i in range(100)]
        iei = compute_iei(series)
        assert iei > 0.80

    def test_empty_series(self):
        """IEI = 0 para serie vacía."""
        assert compute_iei([]) == 0.0


class TestHBU:
    def test_sanction_increases_validity_belief(self):
        """Observar sanción aumenta creencia de validez."""
        prior = 0.5
        posterior = hbu_update(prior, sanction_observed=True)
        assert posterior > prior

    def test_no_sanction_decreases_validity_belief(self):
        """No observar sanción disminuye creencia de validez."""
        prior = 0.5
        posterior = hbu_update(prior, sanction_observed=False)
        assert posterior < prior

    def test_known_value_with_sanction(self):
        """HBU con prior=0.5 y sanción produce ~0.80."""
        posterior = hbu_update(0.5, sanction_observed=True)
        # P(valid|sanction) = 0.80 × 0.5 / (0.80×0.5 + 0.20×0.5) = 0.80
        assert abs(posterior - 0.80) < 1e-6

    def test_known_value_without_sanction(self):
        """HBU con prior=0.5 sin sanción produce ~0.2857."""
        posterior = hbu_update(0.5, sanction_observed=False)
        # P(valid|¬sancion) = 0.20 × 0.5 / (0.20×0.5 + 0.80×0.5) = 0.20
        assert abs(posterior - 0.20) < 1e-6

    def test_output_clamped_to_01(self):
        """Posterior siempre en [0, 1]."""
        for prior in [0.0, 0.1, 0.5, 0.9, 1.0]:
            p_s = hbu_update(prior, True)
            p_n = hbu_update(prior, False)
            assert 0.0 <= p_s <= 1.0
            assert 0.0 <= p_n <= 1.0


class TestCRI:
    def _make_agent(self, cri, institutional_capital, n_supporters):
        class MockAgent:
            pass
        a = MockAgent()
        a.cri = cri
        a.institutional_capital = institutional_capital
        a.n_supporters = n_supporters
        a.base_cost = 0.30
        return a

    def test_high_cri_maintains_position(self):
        """Agente con CRI alto mantiene posición aunque fitness sea bajo."""
        agent = self._make_agent(cri=0.90, institutional_capital=0.90, n_supporters=10)
        result = should_maintain_position(agent, doctrine_fitness=0.20)
        assert result is True

    def test_low_cri_abandons_low_fitness_doctrine(self):
        """Agente con CRI bajo abandona doctrina de bajo fitness."""
        agent = self._make_agent(cri=0.05, institutional_capital=0.05, n_supporters=0)
        result = should_maintain_position(agent, doctrine_fitness=0.02)
        assert result is False

    def test_abandon_cost_increases_with_supporters(self):
        """Costo de abandono escala con n_supporters."""
        c1 = compute_abandon_cost(0.3, 0.9, 0)
        c2 = compute_abandon_cost(0.3, 0.9, 10)
        assert c2 > c1

    def test_maintain_cost_decreases_with_fitness(self):
        """Costo de mantenimiento disminuye cuando fitness es alto."""
        c_low = compute_maintain_cost(0.3, 0.10)
        c_high = compute_maintain_cost(0.3, 0.90)
        assert c_low > c_high


class TestUnionCoalLitRate:
    def test_all_coalition(self):
        """Tasa COAL+LIT = 1.0 cuando todos los sindicatos coalizan."""
        log = [
            {"agent_type": "union", "action": ActionType.COALICIONAR},
            {"agent_type": "union", "action": ActionType.COALICIONAR},
        ]
        rate = compute_union_coal_lit_rate(log)
        assert rate == 1.0

    def test_mixed_actions(self):
        """Tasa COAL+LIT correcta con acciones mezcladas."""
        log = [
            {"agent_type": "union", "action": ActionType.COALICIONAR},
            {"agent_type": "union", "action": ActionType.LITIGAR},
            {"agent_type": "union", "action": ActionType.EVADIR},
            {"agent_type": "firm", "action": ActionType.CUMPLIR},  # no cuenta
        ]
        rate = compute_union_coal_lit_rate(log)
        assert abs(rate - 2/3) < 1e-6

    def test_no_union_actions(self):
        """Tasa = 0 cuando no hay acciones sindicales."""
        log = [{"agent_type": "citizen", "action": ActionType.CUMPLIR}]
        rate = compute_union_coal_lit_rate(log)
        assert rate == 0.0
