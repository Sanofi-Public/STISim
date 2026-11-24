import io
from pathlib import Path

from STISim.agent import Agent
from STISim.config import get_config
from STISim.simulation import _LegacyModuleUnpickler, simulate


def test_legacy_package_name_is_mapped_to_stisim():
    unpickler = _LegacyModuleUnpickler(io.BytesIO())

    loaded_class = unpickler.find_class("ChlamydiaABM.agent", "Agent")

    assert loaded_class is Agent


def test_from_scratch_simulation_writes_time_series(tmp_path):
    config = get_config("config.json")
    config.update(
        {
            "num_agents": 40,
            "numbers_simulations": 1,
            "weeks_start_vaccine": 0,
            "weeks": 4,
            "record_interval": 2,
            "PID_pro_CT_induced": 0.16,
            "vaccine_mechanism": "none",
            "vaccine_mode": "no_vaccine",
        }
    )

    results = simulate(
        config,
        exp_dict={"scenario": "test"},
        load_sims=1,
        output_dir=tmp_path,
        use_saved_initialization=False,
    )

    output_file = Path(tmp_path) / "record_time_series_scenario_test_sim1.parquet"
    assert output_file.exists()
    assert not results.empty
    assert {"week", "id", "state", "age", "gender"}.issubset(results.columns)
