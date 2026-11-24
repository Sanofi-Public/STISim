# STISim

STISim is a Python agent-based simulation framework for studying sexually transmitted infection (STI) transmission, sexual partnership dynamics, screening and treatment pathways, vaccination strategies, and downstream infection-related outcomes.

The framework represents individual agents with demographic, behavioral, infection, treatment, vaccination, and outcome states. Weekly simulation steps update partnerships, transmission, infection progression, intervention effects, aging, and replacement of agents leaving the modeled age range. The current repository uses *Chlamydia trachomatis* as a worked example, including pelvic inflammatory disease (PID) as a downstream outcome, but the model structure is intended to support adaptation to other STIs by modifying disease-specific parameters and progression modules.

## Repository Status

This repository contains research software for running agent-based STI transmission and intervention scenario simulations. The codebase is being prepared for public release and reproducible use. The included example configuration and scenario scripts are based on the agent-based platform developed for a peer-reviewed chlamydia vaccination modeling study published in *Nature Communications*.

## Associated Publication

This codebase is based on the modeling platform described in:

Deng, Q., Ranson, G., Bragazzi, N. L., Bosch Castells, V., Chaves, S. S., Thommes, E., & Wu, J. (2026). An agent-based platform for simulating the impact of chlamydia vaccine in the US population. *Nature Communications*. https://doi.org/10.1038/s41467-026-74025-9

The published study used an agent-based model calibrated to US National Survey of Family Growth (NSFG) and National Health and Nutrition Examination Survey (NHANES) data to evaluate chlamydia vaccination strategies and downstream outcomes, including pelvic inflammatory disease (PID). STISim generalizes this implementation as a reusable STI transmission and intervention modeling framework, with chlamydia vaccination provided as the worked example in this repository.

## Installation

Create a Python environment and install the package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

After installation, run a small from-scratch demonstration:

```bash
python run_minimal_scenario.py
```

This example does not require calibrated saved initialization files and is intended as a quick installation check.

To run the original scenario entry point:

```bash
python run.py
```

The full scenario workflow expects calibrated initialization files and vaccine efficacy decay files in `data_saved/`. The included minimal example allows users to test the STI transmission framework without running the full chlamydia example simulation.

## Data Files

The `data_saved/` directory contains calibration and vaccine efficacy inputs used by the included chlamydia scenario scripts:

- `pool_simulations_withPID.pkl`: saved calibrated initialization data for full chlamydia scenario runs.
- `*_year_decay.csv`: vaccine efficacy decay profiles used by vaccination scenarios.

Simulation outputs are written as Parquet files in `data_saved/` and are ignored by Git. These outputs can be used for downstream analyses of infection prevalence, vaccination status, partner counts, recurrent infection episodes, treatment and screening states, and long-term health outcomes.

## Project Layout

- `STISim/agent.py`: agent state, infection progression, downstream outcome risk, vaccination status, aging and replacement.
- `STISim/relationship.py`: partnership formation, dissolution, and transmission within partnerships.
- `STISim/simulation.py`: weekly simulation loop and output recording.
- `STISim/simulation_setup.py`: experiment parameter combinations and multiprocessing execution.
- `vaccine_scenarios.py`: vaccination policy scenarios and coverage maintenance.
- `config.json`: baseline model parameters.
- `run_minimal_scenario.py`: small runnable example that does not require calibrated inputs.
- `tests/`: unit tests for model components.

## Development

Run tests:

```bash
pytest
```

Check syntax:

```bash
python3 -m py_compile run.py vaccine_scenarios.py STISim/*.py
```

## Citation

If you use STISim, please cite both the software metadata in `CITATION.cff` and the associated *Nature Communications* publication listed above.

## License

This project is released under the Sanofi non-commercial license.
