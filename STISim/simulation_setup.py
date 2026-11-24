from .simulation import simulate
import multiprocessing as mp
import pandas as pd
import copy

def execute_simulation(config, parallelism, exp_key_list, exp_value_comb_list, func):
    concat = []
    config_lists = []    
    tasks = []
    num_sims = 1  # number of simulations loaded from .pkl file; up to 5 here

    for simulation_number in range(1, num_sims + 1):
        for exp_values in exp_value_comb_list:
            # build experiment string
            exp_str = ""
            for i, exp_key in enumerate(exp_key_list):
                exp_str += f"{exp_key}_{exp_values[i]}_"
            exp_str += f"_sim{simulation_number}"
            exp_str = exp_str.strip("_")
            concat.append(exp_str)

            config_copy = copy.deepcopy(config)
            config_lists.append(config_copy)

            # only pass the necessary arguments, no len(tasks) here
            tasks.append((config_copy, exp_key_list, exp_values, func, simulation_number))
    
    # run tasks in parallel
    with mp.Pool(parallelism) as pool:
        pool.starmap(run_simulation, tasks)

    post_process(concat, exp_key_list, exp_value_comb_list, num_sims)


def run_simulation(config, exp_key_list, exp_values, func, load_sims):
    dict_exp = {}
    for exp_key, exp_value in zip(exp_key_list, exp_values):
        config[exp_key] = exp_value
        dict_exp[exp_key] = exp_value

    print(f"Running with dict_exp: {dict_exp} from simulation_number {load_sims}") 
    # by default the function will use the first exp key
    simulate(config, dict_exp, func, exp_key_list[0], load_sims)


def post_process(concat, exp_list, combinations, num_sims):
    dfs = []
    print(f"Number of combinations: {len(combinations)} x {num_sims} simulations")
    print(concat)
    for i, exp_para_str in enumerate(concat):
        print(f"Processing {i+1}th combination")
        df = pd.read_parquet(f"./data_saved/record_time_series_{exp_para_str}.parquet")
        print(f"Post-processing data for {exp_para_str}")
        exp_index = i % len(combinations)

        if len(exp_list) == 1:  # only one experiment parameter
            df[exp_list[0]] = combinations[exp_index][0]
        elif len(exp_list) == 2:  # two experiment parameters
            for j, exp_name in enumerate(exp_list):
                df[exp_name] = combinations[exp_index][j]
        else:
            print("Only support up to 2 experiment parameters")
            return

        dfs.append(df)

    result_df = pd.concat(dfs, ignore_index=True)
    result_df.to_parquet("./data_saved/combined_results.parquet", index=False)
