from .agent import (
    initialize_agents_parallel,
    update_agent_states,
    age_and_replace_agents
)


from .relationship import (
    form_relationships,
    dissolve_relationships,
    infection_occurs_in_relationships
)

import pandas as pd
from copy import deepcopy
import random
import pickle
import numpy as np
from pathlib import Path


class _LegacyModuleUnpickler(pickle.Unpickler):
    """Load initialization files created before ChlamydiaABM became STISim."""

    _MODULE_ALIASES = {
        "ChlamydiaABM.agent": "STISim.agent",
    }

    def find_class(self, module, name):
        module = self._MODULE_ALIASES.get(module, module)
        return super().find_class(module, name)


def count_SEIR(
    agents, susceptible, infected_asymptomatic, infected_symptomatic, recover
):
    # Initialize counters
    susceptible_count = 0
    infected_asymptomatic_count = 0
    infected_symptomatic_count = 0
    recover_count = 0

    for agent in agents:
        if agent.state == "S":
            susceptible_count += 1
        elif agent.state == "E":
            infected_asymptomatic_count += 1
        elif agent.state == "I":
            infected_symptomatic_count += 1
        elif agent.state == "R":
            recover_count += 1

    # append the counts to the respective lists
    susceptible.append(susceptible_count)
    infected_asymptomatic.append(infected_asymptomatic_count)
    infected_symptomatic.append(infected_symptomatic_count)
    recover.append(recover_count)

def sexual_network(agents, config, susceptible, infected_symptomatic, infected_asymptomatic, recover, week):
        
    form_relationships(agents, config, week)
    infection_occurs_in_relationships(agents, config, week)
    update_agent_states(agents, config, week)
    dissolve_relationships(agents, config)
    update_agents = age_and_replace_agents(agents, config, week)
    agents = update_agents
    count_SEIR(
        agents,
        susceptible=susceptible,
        infected_symptomatic=infected_symptomatic,
        infected_asymptomatic=infected_asymptomatic,
        recover=recover,
    )
    return agents

def load_simulation(file_path, load_sims):

    with open(file_path, "rb") as f:
        simulations = _LegacyModuleUnpickler(f).load()
    selected_sim = next(sim for sim in simulations if sim["simulation_number"] == load_sims)

    return (
        selected_sim["agents"],
        selected_sim["config"],
        selected_sim["random_state"],
        selected_sim["numpy_state"]
    )


def _default_pid_probability():
    return {
        (15, 19): 0.00005,
        (20, 24): 0.00005,
        (25, 29): 0.000015,
        (30, 34): 0.000015,
        (35, 39): 0.00001,
        (40, 44): 0.00001,
        (45, 54): 0.00001,
    }


def _prepare_config(config):
    prepared = deepcopy(config)
    prepared.setdefault("infection_probability_per_contact_female", 0.33)
    prepared.setdefault("PID_probability", _default_pid_probability())
    prepared.setdefault("PID_pro_CT_induced", 0.16)
    prepared.setdefault("vaccine_mechanism", "none")
    prepared.setdefault("vaccine_mode", "no_vaccine")
    prepared.setdefault("vaccination_coverage", 0.0)
    prepared.setdefault("vaccine_efficacy", 0.0)
    prepared.setdefault("vaccine_efficacy_expo", np.zeros(prepared.get("weeks", 1) + 2))
    return prepared


def _experiment_string(exp_dict, load_sims):
    parts = [f"{key}_{value}" for key, value in exp_dict.items()]
    parts.append(f"sim{load_sims}")
    return "_".join(parts)


def _record_agent(time_series_data, agent, load_sims, simulation_number, week):
    time_series_data.append({
        'load_sims': load_sims,
        'simulation_number': simulation_number,
        'week': week,
        "id": agent.id,
        'gender': agent.gender,
        'age': agent.age,
        "num_partners": len(agent.existing_partners),
        'sexual_behavior': agent.sexual_behavior,
        'dnp': agent.dnp,
        'preferred_duration': agent.preferred_duration,
        'state': agent.state,
        'gap_time': agent.gap_time,
        'immunity': agent.immunity,
        'sick_period': agent.sick_period,
        'weeks_until_treatment': agent.weeks_until_treatment,
        'infectious_period': agent.infectious_period,
        'recovery_period': agent.recovery_period,
        'vaccined': agent.vaccined,
        'vaccined_period': agent.vaccined_period,
        'seeks_treatment': agent.seeks_treatment,
        'screened': agent.screened,
        'detected': agent.detected,
        'PID_risk_untreated': agent.PID_risk_untreated,
        'CT_episodes_count': agent.CT_episodes_count,
        'PID': agent.PID,
        'PID_onset_age': agent.PID_onset_age,
        'PID_onset_week': agent.PID_onset_week,
        'had_treated_CT': agent.had_treated_CT,
        'had_vaccine': agent.had_vaccine,
        'weeks_since_vaccine': agent.weeks_since_vaccine,
        'number_of_partners': agent.number_of_partners,
        'PID_episodes_count': agent.PID_episodes_count,
        'PID_from_CT': agent.PID_from_CT,
        'current_VE': agent.current_efficacy
    })


def simulate(
    config,
    exp_dict=None,
    func=None,
    func_value_key=None,
    load_sims=1,
    input_data_path="./data_saved/pool_simulations_withPID.pkl",
    output_dir="./data_saved",
    use_saved_initialization=True,
):
    exp_dict = exp_dict or {}
    susceptible = []
    infected_asymptomatic = []
    infected_symptomatic = []
    recover = []
    time_series_data = []

    input_data_path = Path(input_data_path)
    if use_saved_initialization:
        if not input_data_path.exists():
            raise FileNotFoundError(
                f"Saved initialization file not found: {input_data_path}. "
                "Set use_saved_initialization=False for a from-scratch run."
            )
        base_agents, base_config, base_random_state, base_numpy_state = load_simulation(
            input_data_path, load_sims
        )
        base_config = _prepare_config(base_config)
        max_id = max(agent.id for agent in base_agents)
        random.setstate(base_random_state)
        np.random.set_state(base_numpy_state)

        for key, value in config.items():
            base_config[key] = value
    else:
        base_config = _prepare_config(config)
        from .agent import Agent
        Agent._id_counter = 1
        base_agents = initialize_agents_parallel(base_config, current_week=0)
        max_id = max(agent.id for agent in base_agents)

    for i in range(config["numbers_simulations"]):

        #======load .pkl file======
        from .agent import Agent
        Agent._id_counter = max_id + 1
        print(f"Simulation {i+1} starts with Agent._id_counter={Agent._id_counter}")
        agents = deepcopy(base_agents)
        sim_config = deepcopy(base_config)
        count_SEIR(agents, 
                    susceptible, 
                    infected_asymptomatic, 
                    infected_symptomatic, 
                    recover)
        susceptible = deepcopy(susceptible)
        infected_asymptomatic = deepcopy(infected_asymptomatic)
        infected_symptomatic = deepcopy(infected_symptomatic)
        recover = deepcopy(recover)

        #======formal simulation======
        for week in range(1, config['weeks_start_vaccine'] + config["weeks"] +1):
            sim_config["current_week"] = week      
            for agent in agents:
                agent.age += 1/52
                if agent.age > agent.age_group[1] and agent.age <= 54:
                    if agent.age_group[1] == 44:
                        updated_group = (agent.age_group[0] + 5, 54)
                    else:
                        updated_group = (agent.age_group[0] + 5, agent.age_group[1] + 5)
                    agent.age_group = updated_group
                    
            #======vaccination function======
            if func is not None and func_value_key is not None and week == config['weeks_start_vaccine']:
                func(agents, sim_config, exp_dict[func_value_key], week)
            #======vaccination function======

            updated_agents = sexual_network(agents, 
                            sim_config, 
                            susceptible = susceptible, 
                            infected_symptomatic = infected_symptomatic, 
                            infected_asymptomatic = infected_asymptomatic, 
                            recover = recover, 
                            week = week)
            agents = updated_agents
            
            if func is not None and func_value_key is not None and week >= config['weeks_start_vaccine']:
                from vaccine_scenarios import filter_agents_based_on_group
                filter_agents_based_on_group(agents, sim_config, exp_dict[func_value_key])
                
            if week == 1 or week % config['record_interval'] == 0 or week == config["weeks"] + config['weeks_start_vaccine']:
                for agent in agents:
                    _record_agent(time_series_data, agent, load_sims, i + 1, week)
            if (week) % 52 == 0:
                print(f"Simulation {i + 1} has been running for {(week) // 52} years")    
    
    df_time_series = pd.DataFrame(time_series_data)
    exp_para = _experiment_string(exp_dict, load_sims)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = output_dir / f"record_time_series_{exp_para}.parquet"
    df_time_series.to_parquet(file_name, index=False, compression="snappy")
    return df_time_series
