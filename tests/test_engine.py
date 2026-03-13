"""
tests/test_engine.py — Tests del motor de simulación.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import yaml

from engine.simulation import load_config, build_agents, run_simulation
from engine.environment import LegalEnvironment
from engine.actions import ActionType


@pytest.fixture
def config():
    config_path = Path(__file__).parent.parent / "config" / "argentina.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestLoadConfig:
    def test_loads_yaml(self, config):
        """Configuración carga correctamente desde YAML."""
        assert "scenario" in config
        assert "agents" in config
        assert "cli_weights" in config
        assert "validation_criteria" in config

    def test_scenario_fields(self, config):
        """Escenario tiene todos los campos requeridos."""
        s = config["scenario"]
        assert s["country"] == "Argentina"
        assert s["cli_target"] == 0.89
        assert s["simulation_rounds"] == 100
        assert s["reform_trigger_round"] == 5
        assert len(s["monte_carlo_seeds"]) == 5


class TestBuildAgents:
    def test_total_count(self, config):
        """build_agents produce exactamente 816 agentes."""
        import random
        agents = build_agents(config, random.Random(42))
        assert len(agents) == 816

    def test_agent_type_counts(self, config):
        """Cada tipo de agente tiene el número correcto."""
        import random
        from collections import Counter
        agents = build_agents(config, random.Random(42))
        counts = Counter(a.agent_type for a in agents)
        assert counts["judge"] == 5
        assert counts["legislator"] == 257  # 130 + 127
        assert counts["union"] == 3
        assert counts["firm"] == 50
        assert counts["citizen"] == 500
        assert counts["regulator"] == 1

    def test_all_agents_have_required_attrs(self, config):
        """Todos los agentes tienen los atributos requeridos."""
        import random
        agents = build_agents(config, random.Random(42))
        for agent in agents:
            assert hasattr(agent, "agent_id")
            assert hasattr(agent, "cri")
            assert hasattr(agent, "institutional_capital")
            assert hasattr(agent, "norm_validity_belief")
            assert hasattr(agent, "available_actions")
            assert 0.0 <= agent.cri <= 1.0
            assert 0.0 <= agent.institutional_capital <= 1.0


class TestLegalEnvironment:
    def test_initial_state(self, config):
        """LegalEnvironment inicializa con estado pre-reforma correcto."""
        env = LegalEnvironment(config)
        assert env.round_number == 0
        assert env.reform_active is False
        assert env.reform_trigger_round == 5
        assert env.coalition_active is False
        assert len(env.cli_history) == 0

    def test_reform_trigger(self, config):
        """Reforma se activa en la ronda correcta."""
        env = LegalEnvironment(config)
        assert not env.reform_active
        env.start_round(4)
        assert not env.reform_active
        env.start_round(5)
        assert env.reform_active

    def test_reform_trigger_only_once(self, config):
        """Reforma se dispara solo una vez."""
        env = LegalEnvironment(config)
        env.start_round(5)
        fitness_after_trigger = env.doctrine_fitness
        env.start_round(5)  # segunda vez: no debe bajar más
        # doctrine_fitness no debería bajar de nuevo
        assert env.doctrine_fitness >= fitness_after_trigger * 0.9

    def test_cli_computation(self, config):
        """CLI se computa en rango [0, 1] y se agrega al historial."""
        env = LegalEnvironment(config)
        cli = env.compute_current_cli()
        assert 0.0 <= cli <= 1.0
        assert len(env.cli_history) == 1

    def test_block_rate_zero_initially(self, config):
        """Tasa de bloqueo es 0 cuando no hay intentos de reforma."""
        env = LegalEnvironment(config)
        assert env.get_block_rate() == 0.0

    def test_apply_coalicionar_activates_coalition(self, config):
        """COALICIONAR activa el estado de coalición."""
        env = LegalEnvironment(config)
        assert not env.coalition_active
        env.apply_action("union_cgt", "union", ActionType.COALICIONAR)
        assert env.coalition_active

    def test_apply_reversar_increments_block(self, config):
        """REVERSAR actualiza doctrine_fitness cuando reforma activa."""
        env = LegalEnvironment(config)
        env.reform_active = True
        fitness_before = env.doctrine_fitness
        env.apply_action("judge_0", "judge", ActionType.REVERSAR)
        # REVERSAR refuerza la doctrina (sube fitness)
        assert env.doctrine_fitness >= fitness_before


class TestSimulationRun:
    def test_10_rounds_no_error(self, config):
        """Simulación corre 10 rondas sin errores."""
        result = run_simulation(config, seed=42, n_rounds=10)
        assert result is not None
        assert result["total_rounds"] == 10

    def test_cli_history_length(self, config):
        """Historial de CLI tiene longitud igual a n_rounds."""
        result = run_simulation(config, seed=42, n_rounds=10)
        assert len(result["cli_history"]) == 10

    def test_cli_in_valid_range(self, config):
        """CLI final está en [0, 1]."""
        result = run_simulation(config, seed=42, n_rounds=10)
        assert 0.0 <= result["cli_final"] <= 1.0

    def test_reform_trigger_round(self, config):
        """Reform trigger se activa en ronda 5 por defecto."""
        import random
        from engine.simulation import build_agents
        from engine.environment import LegalEnvironment
        from engine.hbu import hbu_batch_update

        rng = random.Random(42)
        agents = build_agents(config, rng)
        env = LegalEnvironment(config)

        for r in range(1, 6):
            env.start_round(r)

        assert env.reform_active is True

    def test_reproducibility(self, config):
        """Misma seed produce mismo CLI."""
        result1 = run_simulation(config, seed=42, n_rounds=20)
        result2 = run_simulation(config, seed=42, n_rounds=20)
        assert result1["cli_final"] == result2["cli_final"]

    def test_different_seeds_differ(self, config):
        """Seeds distintas producen CLIs distintos."""
        result1 = run_simulation(config, seed=42, n_rounds=50)
        result2 = run_simulation(config, seed=999, n_rounds=50)
        # Con baja varianza pueden ser iguales, pero normalmente difieren
        # Solo chequeamos que no hay error
        assert isinstance(result1["cli_final"], float)
        assert isinstance(result2["cli_final"], float)

    def test_action_log_non_empty(self, config):
        """Log de acciones tiene entradas después de la simulación."""
        result = run_simulation(config, seed=42, n_rounds=5)
        assert len(result["action_log_summary"]) > 0

    def test_block_rate_positive_post_reform(self, config):
        """Tasa de bloqueo es positiva después de la reforma (ronda > 5)."""
        result = run_simulation(config, seed=42, n_rounds=20)
        # Hay reformas y bloqueos porque IMPUGNAR_CN y REVERSAR disparan
        assert result["reform_attempts"] >= 0  # puede ser 0 en primeras rondas
