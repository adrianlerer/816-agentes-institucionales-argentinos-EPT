"""
tests/test_agents.py — Tests de instanciación y comportamiento de agentes.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from agents.base import BaseLegalAgent
from agents.judge import JudgeAgent
from agents.legislator import LegislatorAgent
from agents.union import UnionAgent
from agents.firm import RegulatedFirmAgent
from agents.citizen import CitizenAgent
from agents.regulator import RegulatorAgent
from engine.actions import ActionType
from engine.environment import LegalEnvironment


@pytest.fixture
def rng():
    return random.Random(42)


@pytest.fixture
def config():
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "argentina.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def env(config):
    return LegalEnvironment(config)


class TestJudgeAgent:
    def test_instantiation(self, rng):
        """JudgeAgent instancia correctamente con parámetros CSJN."""
        judge = JudgeAgent("judge_0", cri=0.78, institutional_capital=0.90, rng=rng)
        assert judge.agent_id == "judge_0"
        assert judge.cri == 0.78
        assert judge.institutional_capital == 0.90
        assert judge.agent_type == "judge"

    def test_available_actions(self, rng):
        """JudgeAgent tiene exactamente 3 acciones disponibles."""
        judge = JudgeAgent("judge_0", cri=0.78, institutional_capital=0.90, rng=rng)
        assert ActionType.SANCIONAR in judge.available_actions
        assert ActionType.REVERSAR in judge.available_actions
        assert ActionType.IMPUGNAR_CN in judge.available_actions
        assert len(judge.available_actions) == 3

    def test_decide_action_returns_valid(self, rng, env):
        """JudgeAgent.decide_action retorna ActionType válido."""
        judge = JudgeAgent("judge_0", cri=0.78, institutional_capital=0.90, rng=rng)
        action = judge.decide_action(env)
        assert isinstance(action, ActionType)
        assert action in judge.available_actions

    def test_judge_reverses_when_reform_active_low_fitness(self, rng, config):
        """Juez elige REVERSAR cuando reforma activa y fitness bajo."""
        env = LegalEnvironment(config)
        env.reform_active = True
        env.doctrine_fitness = 0.30  # bajo el threshold 0.60
        judge = JudgeAgent("judge_0", cri=0.78, institutional_capital=0.90, rng=rng)
        action = judge.decide_action(env)
        assert action == ActionType.REVERSAR

    def test_judge_sanctions_without_reform(self, rng, env):
        """Juez elige SANCIONAR cuando no hay reforma activa."""
        judge = JudgeAgent("judge_0", cri=0.78, institutional_capital=0.90, rng=rng)
        assert not env.reform_active
        action = judge.decide_action(env)
        assert action == ActionType.SANCIONAR


class TestLegislatorAgent:
    def test_oficialismo_instantiation(self, rng):
        """LegislatorAgent oficialismo instancia correctamente."""
        leg = LegislatorAgent(
            "leg_of_0", cri=0.30, institutional_capital=0.40,
            party_discipline=0.80, reform_preference=0.70,
            is_oficialismo=True, rng=rng,
        )
        assert leg.is_oficialismo is True
        assert leg.cri == 0.30
        assert ActionType.REFORMAR in leg.available_actions

    def test_oposicion_instantiation(self, rng):
        """LegislatorAgent oposición instancia correctamente."""
        leg = LegislatorAgent(
            "leg_op_0", cri=0.60, institutional_capital=0.50,
            party_discipline=0.70, reform_preference=0.20,
            is_oficialismo=False, rng=rng,
        )
        assert leg.is_oficialismo is False
        assert ActionType.IMPUGNAR_CN in leg.available_actions

    def test_decide_action_valid(self, rng, env):
        """LegislatorAgent retorna ActionType válido."""
        leg = LegislatorAgent(
            "leg_of_0", cri=0.30, institutional_capital=0.40,
            party_discipline=0.80, reform_preference=0.70,
            is_oficialismo=True, rng=rng,
        )
        action = leg.decide_action(env)
        assert isinstance(action, ActionType)
        assert action in leg.available_actions


class TestUnionAgent:
    def test_cgt_instantiation(self, rng):
        """UnionAgent CGT instancia con parámetros correctos."""
        union = UnionAgent(
            "union_cgt", union_name="CGT", cri=0.85,
            institutional_capital=0.80, coalition_capacity=0.95,
            strike_capacity=0.90, legal_resources=0.85,
            available_actions=[ActionType.COALICIONAR, ActionType.LITIGAR, ActionType.EVADIR],
            rng=rng,
        )
        assert union.cri == 0.85
        assert union.coalition_capacity == 0.95
        assert union.union_name == "CGT"

    def test_union_prefers_coalicionar_post_reform(self, rng, config):
        """Sindicato prefiere COALICIONAR cuando la reforma está activa."""
        env = LegalEnvironment(config)
        env.reform_active = True
        union = UnionAgent(
            "union_cgt", union_name="CGT", cri=0.85,
            institutional_capital=0.80, coalition_capacity=0.95,
            strike_capacity=0.90, legal_resources=0.85,
            available_actions=[ActionType.COALICIONAR, ActionType.LITIGAR, ActionType.EVADIR],
            rng=rng,
        )
        action = union.decide_action(env)
        assert action in (ActionType.COALICIONAR, ActionType.LITIGAR)

    def test_decide_action_valid(self, rng, env):
        """UnionAgent retorna ActionType válido."""
        union = UnionAgent(
            "union_cta", union_name="CTA", cri=0.80,
            institutional_capital=0.70, coalition_capacity=0.85,
            strike_capacity=0.80, legal_resources=0.75,
            available_actions=[ActionType.COALICIONAR, ActionType.LITIGAR],
            rng=rng,
        )
        action = union.decide_action(env)
        assert isinstance(action, ActionType)


class TestRegulatedFirmAgent:
    def test_instantiation(self, rng):
        """RegulatedFirmAgent instancia correctamente."""
        firm = RegulatedFirmAgent(
            "firm_0", cri=0.20, institutional_capital=0.30,
            capture_capacity=0.40, rng=rng,
        )
        assert firm.cri == 0.20
        assert firm.capture_capacity == 0.40
        assert ActionType.CUMPLIR in firm.available_actions
        assert ActionType.CAPTURAR in firm.available_actions

    def test_decide_action_valid(self, rng, env):
        """RegulatedFirmAgent retorna ActionType válido."""
        firm = RegulatedFirmAgent(
            "firm_0", cri=0.20, institutional_capital=0.30,
            capture_capacity=0.40, rng=rng,
        )
        action = firm.decide_action(env)
        assert isinstance(action, ActionType)
        assert action in firm.available_actions


class TestCitizenAgent:
    def test_instantiation(self, rng):
        """CitizenAgent instancia con solo 2 acciones."""
        citizen = CitizenAgent(
            "citizen_0", cri=0.15, institutional_capital=0.10,
            coalition_capacity=0.20, rng=rng,
        )
        assert citizen.cri == 0.15
        assert len(citizen.available_actions) == 2
        assert ActionType.CUMPLIR in citizen.available_actions
        assert ActionType.EVADIR in citizen.available_actions

    def test_decide_action_valid(self, rng, env):
        """CitizenAgent retorna ActionType válido."""
        citizen = CitizenAgent(
            "citizen_0", cri=0.15, institutional_capital=0.10,
            coalition_capacity=0.20, rng=rng,
        )
        action = citizen.decide_action(env)
        assert action in (ActionType.CUMPLIR, ActionType.EVADIR)


class TestRegulatorAgent:
    def test_instantiation(self, rng):
        """RegulatorAgent instancia correctamente."""
        reg = RegulatorAgent(
            "regulator_0", cri=0.40, institutional_capital=0.60,
            capture_vulnerability=0.50, rng=rng,
        )
        assert reg.cri == 0.40
        assert reg.capture_vulnerability == 0.50
        assert not reg.is_captured

    def test_capture_mechanism(self, rng):
        """Regulador puede ser capturado con probabilidad correcta."""
        reg = RegulatorAgent(
            "regulator_0", cri=0.40, institutional_capital=0.60,
            capture_vulnerability=1.0, rng=random.Random(0),
        )
        # Con vulnerabilidad=1.0 y capture_capacity=1.0, siempre capturado
        captured = reg.receive_capture_attempt(capture_capacity=1.0)
        assert captured is True
        assert reg.is_captured is True

    def test_decide_action_always_sancionar(self, rng, env):
        """Regulador siempre retorna SANCIONAR."""
        reg = RegulatorAgent(
            "regulator_0", cri=0.40, institutional_capital=0.60,
            capture_vulnerability=0.50, rng=rng,
        )
        action = reg.decide_action(env)
        assert action == ActionType.SANCIONAR
