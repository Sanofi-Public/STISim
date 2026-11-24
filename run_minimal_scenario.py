"""Run a small STISim simulation without calibrated pickle inputs.

This example is intended for installation checks. It uses the same model
mechanisms as the larger scenarios, but with a small population and short time
horizon so it can run quickly.
"""

from pathlib import Path

from STISim.config import get_config
from STISim.simulation import simulate


PROJECT_ROOT = Path(__file__).resolve().parent


def main():
    config = get_config(PROJECT_ROOT / "config.json")
    config.update(
        {
            "num_agents": 200,
            "numbers_simulations": 1,
            "weeks_start_vaccine": 0,
            "weeks": 52,
            "record_interval": 13,
            "PID_pro_CT_induced": 0.16,
            "vaccine_mechanism": "none",
            "vaccine_mode": "no_vaccine",
        }
    )

    output_dir = PROJECT_ROOT / "data_saved" / "example_outputs"
    results = simulate(
        config,
        exp_dict={"scenario": "minimal_no_vaccine"},
        load_sims=1,
        output_dir=output_dir,
        use_saved_initialization=False,
    )

    print(f"Wrote {len(results)} records to {output_dir}")


if __name__ == "__main__":
    main()
