"""
tests/test_validation.py — Tests de validación Monte Carlo e histórica.

816 Agentes Institucionales Argentinos: Simulación EPT
Lerer (2026) | AGPL-3.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import yaml

from engine.simulation import run_simulation
from validation.monte_carlo import run_monte_carlo, check_validation_criteria
from validation.historical import (
    load_historical_reforms,
    compute_historical_block_rate,
    validate_against_history,
)
from validation.emergent_cli import verify_emergent_cli


@pytest.fixture
def config():
    config_path = Path(__file__).parent.parent / "config" / "argentina.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestMonteCarloSingleSeed:
    def test_single_seed_cli_in_range(self, config):
        """Una seed produce CLI en el rango publicado [0.80, 0.95]."""
        result = run_simulation(config, seed=42, n_rounds=100)
        assert 0.80 <= result["cli_final"] <= 0.95

    def test_single_seed_block_rate_positive(self, config):
        """Una seed produce CLI > 0 despues de la reforma."""
        result = run_simulation(config, seed=42, n_rounds=100)
        assert result["cli_final"] > 0.0


class TestMonteCarloFull:
    def test_5_seeds_run_without_error(self, config):
        """Monte Carlo completo (5 seeds x 100 rondas) termina sin error."""
        mc = run_monte_carlo(config, n_rounds=100, print_progress=False)
        assert len(mc["results"]) == 5

    def test_cli_mean_in_range(self, config):
        """CLI medio de 5 seeds esta en rango publicado [0.80, 0.95]."""
        mc = run_monte_carlo(config, n_rounds=100, print_progress=False)
        assert 0.80 <= mc["cli_mean"] <= 0.95

    def test_all_checks_pass(self, config):
        """Los 4 criterios de validacion pasan."""
        mc = run_monte_carlo(config, n_rounds=100, print_progress=False)
        checks = check_validation_criteria(
            mc,
            config["validation_criteria"],
            cli_target=config["scenario"]["cli_target"],
        )
        assert len(checks) == 4
        for check in checks:
            assert check["passed"], (
                f"Criterio '{check['name']}' fallo: {check['message']}"
            )

    def test_cli_std_low(self, config):
        """Desviacion estandar del CLI es baja (atractor fuerte)."""
        mc = run_monte_carlo(config, n_rounds=100, print_progress=False)
        assert mc["cli_std"] < 0.05


class TestValidationCriteriaChecker:
    def test_checker_structure(self, config):
        """Checker retorna 4 items con campos requeridos."""
        mc = run_monte_carlo(config, n_rounds=10, print_progress=False)
        checks = check_validation_criteria(
            mc, config["validation_criteria"]
        )
        assert len(checks) == 4
        for c in checks:
            assert "name" in c
            assert "value" in c
            assert "passed" in c
            assert "message" in c

    def test_checker_with_bad_cli(self, config):
        """Checker falla correctamente si CLI esta fuera de rango."""
        bad_mc = {
            "cli_mean": 0.20,
            "cli_std": 0.01,
            "block_rate_mean": 0.95,
            "union_coal_lit_mean": 0.65,
            "seeds": [42],
            "n_rounds": 100,
            "results": [],
            "cli_history_mean": [],
        }
        checks = check_validation_criteria(
            bad_mc, config["validation_criteria"]
        )
        cli_check = next(c for c in checks if "CLI" in c["name"] and "[" in c["name"])
        assert cli_check["passed"] is False


class TestHistoricalValidation:
    def test_csv_loads(self):
        """CSV de reformas historicas carga correctamente."""
        reforms = load_historical_reforms("data/historical_reforms.csv")
        assert len(reforms) == 23

    def test_csv_has_required_columns(self):
        """CSV tiene todas las columnas requeridas."""
        reforms = load_historical_reforms("data/historical_reforms.csv")
        required_cols = [
            "reform_id", "year", "government", "reform_name",
            "final_outcome",
        ]
        for col in required_cols:
            assert col in reforms[0], f"Columna faltante: {col}"

    def test_historical_block_rate_above_60(self):
        """Tasa de bloqueo histórica es > 60% (blocked+reversed+partial = 15/23 = 65.2%)."""
        reforms = load_historical_reforms("data/historical_reforms.csv")
        rate = compute_historical_block_rate(reforms)
        # 15/23 = 65.2%: blocked(3) + reversed(5) + partial(7)
        assert rate >= 0.60

    def test_validate_against_history(self, config):
        """Validacion historica retorna estructura correcta."""
        result = run_simulation(config, seed=42, n_rounds=100)
        validation = validate_against_history(
            result["block_rate"],
            csv_path="data/historical_reforms.csv",
        )
        assert validation["n_reforms"] == 23
        assert validation["historical_block_rate"] is not None


class TestEmergentCLI:
    def test_emergent_verification(self, config):
        """CLI emerge sin depender del target en la configuracion."""
        result = verify_emergent_cli(config, seed=42, n_rounds=100)
        assert result["is_emergent"] is True, result["message"]

    def test_cli_without_target_in_range(self, config):
        """CLI sin target sigue en [0.80, 0.95]."""
        result = verify_emergent_cli(config, seed=42, n_rounds=100)
        assert 0.80 <= result["cli_without_target"] <= 0.95
