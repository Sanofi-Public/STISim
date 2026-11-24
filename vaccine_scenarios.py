import random
import numpy as np

from STISim.config import get_config
from STISim.simulation_setup import execute_simulation
from itertools import product



"""scenario 1"""
#===================scenario 1: simple test with vaccine or without vaccine===================
def scenario_1():
    # set up parallelism
    parallelism = 1

    # set up initializations
    config = get_config("config.json")

    # set up configurations
    config["PID_pro_CT_induced"] = 0.16

    config["vaccine_efficacy_expo"] = np.loadtxt(
    "./data_saved/10_year_decay.csv",
    delimiter=",")

    # set up experiment parameters
    input_exp_key = "vaccine_mechanism"
    input_exp_values = ["no_vaccine", "susceptibility_only", "infectiousness_only", "both"]
    exp_key_list = [input_exp_key]
    exp_value_comb_list = list(product(input_exp_values))

    # execute the simulation
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_vaccine_mechanism,
    )

def change_vaccine_mechanism(agents, config, mechanism, week):
    config["vaccine_mode"] = mechanism

    if mechanism == "no_vaccine":
        config["vaccination_coverage"] = 0
        config["vaccine_mechanism"] = "none"
        for agent in agents:
            agent.vaccined = False       
    else:
        config["vaccine_mechanism"] = mechanism
        config["vaccination_coverage"] = 0.6
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # average of 20 years of vaccine duration
                   
#===================scenario 1: simple test with vaccine or without vaccine===================


"""scenario 2"""
#===================scenario 2: coimpact of vaccine efficacy and vaccine coverage===================
def scenario_2():
    # set up parallelism
    # sys.setrecursionlimit(10000)
    parallelism = 18

    # set up configurations
    config = get_config("config.json")
    config["PID_pro_CT_induced"] = 0.16

    # set up experiment parameters
    exp_para1_key = "vaccination_coverage" 
    exp_para1_values = np.round(np.linspace(0, 1, 6), 1) # base line 0.2
    
    
    exp_para2_key = "vaccine_efficacy" 
    exp_para2_values = np.round(np.linspace(0, 1, 6), 1)  # base line 0.8  
    

    exp_key_list = [exp_para1_key, exp_para2_key] 
    exp_value_comb_list = list(product(exp_para1_values, exp_para2_values))
    print(f"Experiment keys: {exp_key_list}")
    print(f"Experiment value combinations: {exp_value_comb_list}")

    # execute the simulation
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_vaccine,
    )

def change_vaccine(agents, config, efficacy, week):
    config["vaccine_mechanism"] = "susceptibility_only"
    config["vaccine_mode"] = "Not_changed"

    for agent in agents:
        if agent.age <= 44 and not agent.had_vaccine:
            if random.random() < config['vaccination_coverage']:
                agent.vaccined = True
                agent.had_vaccine = True
                agent.vaccined_period = config['weeks']  # years of vaccine duration
                agent.current_efficacy = config["vaccine_efficacy"]
#===================scenario 2: coimpact of vaccine efficacy and vaccine coverage===================


"""scenario 3"""
#========================scenario 3: vaccine priority =====================
def scenario_3():
    # set up parallelism
    parallelism = 2

    # set up configurations
    config = get_config("config.json")
    config["PID_pro_CT_induced"] = 0.16
    config["vaccine_efficacy_expo"] = np.loadtxt(
    "./data_saved/10_year_decay.csv",
    delimiter=",")
    
    # set up experiment parameters
    input_exp_key = "vaccine_priority"  # experiment parameter 1 key
    input_exp_values = [
        "no_vaccine",
        "60%_female_male"
    ]
    # input_exp_values = [
    #     "no_vaccine",
    #     "60%_age-15-24",
    #     "60%_age-25-44",
    #     "90%_age-15-24",
    #     "90%_age-25-44",
    #     "60%_female",
    #     "60%_female_male",
    #     "90%_female",
    #     "90%_female_male",
    # ]  # experiment parameter 1 values
    print(f"Parameters: {input_exp_key}:")
    exp_key_list = [input_exp_key]
    exp_value_comb_list = list(product(input_exp_values))

    # execute the simulation
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_vaccination_coverage,
    )

def change_vaccination_coverage(agents, config, priority, week):
    config["vaccine_mode"] = priority
    config["vaccine_mechanism"] = (
        "none" if priority == "no_vaccine" else "susceptibility_only"
    )

    if priority == "no_vaccine":  # no_vaccine    
        config["vaccination_coverage"] = 0  
        for agent in agents:
            agent.vaccined = False

    if priority == "60%_age-15-24":  # age-15-24 60% coverage 
        config["vaccination_coverage"] = 0.6    
        for agent in agents:
            if agent.age <= 24:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
            
    if priority == "60%_age-25-44":  # age-25-44 60% coverage
        config["vaccination_coverage"] = 0.6
        for agent in agents:
            if agent.age >= 25 and agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
            
    if priority == "90%_age-15-24":  # age-15-24  90% coverage
        config["vaccination_coverage"] = 0.9
        for agent in agents:
            if agent.age <= 24:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration

    if priority == "90%_age-25-44":  # age-25-44  90% coverage  
        config["vaccination_coverage"] = 0.9      
        for agent in agents:
            if agent.age >= 25 and agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True 
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
            
    if priority == "60%_female":  #female in ages 15-44 only 60% coverage
        config["vaccination_coverage"] = 0.6        
        for agent in agents:
            if agent.gender == "female" and agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True 
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
            
    if priority == "60%_female_male":  # female and male in ages 15-44 60% coverage
        config["vaccination_coverage"] = 0.6       
        for agent in agents:
            if agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration

    if priority == "90%_female":  # female in ages 15-44 only 90% coverage 
        config["vaccination_coverage"] = 0.9      
        for agent in agents:
            if agent.gender == "female" and agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True 
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks']

    if priority == "90%_female_male":  # female and male in ages 15-44  90% coverage      
        config["vaccination_coverage"] = 0.9
        for agent in agents:
            if agent.age <= 44:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True 
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
#========================scenario 3: vaccine priority =====================

def filter_agents_based_on_group(agents, config, scenarios):
    # print(f"[DEBUG] Enter filter_agents_based_on_group with scenarios={scenarios}, type={type(scenarios)}")
    vaccined_agents = []
    non_vaccined_agents = []
    total_agents = 0 
   
    if isinstance(scenarios, (float, int, np.floating)):

        coverage = float(config.get("vaccination_coverage", 0.0))
        efficacy = float(config.get("vaccine_efficacy", 0.0))
        total_agents = 0
        for agent in agents:
            if agent.age <= 44:
                total_agents += 1
                if agent.vaccined:
                    vaccined_agents.append(agent)
                else:
                    non_vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, coverage, config, scenario_type="scenario_2")
        # print(f"[DEBUG] scenario_2 adjustment: coverage={coverage}, efficacy={efficacy}, total_agents={total_agents}")

    if scenarios == "no_vaccine":  # no_vaccine    
        config["vaccination_coverage"] = 0  
        for agent in agents:
            agent.vaccined = False

    if scenarios in ["susceptibility_only", 
                    "infectiousness_only", 
                    "both", 
                    "duration_of_1_years",
                    "duration_of_5_years",
                    "duration_of_10_years",
                    "duration_of_15_years",
                    "duration_of_20_years",
                    "Not_changed",
                    "immediate_scale_up"
                    ]:  # vaccine efficacy
        config["vaccination_coverage"] = 0.6
        for agent in agents:
            if agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")  

    if scenarios in [
       "5_years_scale_up",
        "10_years_scale_up",
        "20_years_scale_up", 
    ]:
        coverage = scale_up_coverage(config)
        config["vaccination_coverage"] = coverage
        for agent in agents:
            if agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")  
    
    if scenarios == "60%_age-15-24":  # age-15-24 60% coverage 
        config["vaccination_coverage"] = 0.6            
        for agent in agents:
            if agent.age <= 24:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")  
                            
    if scenarios == "60%_age-25-44":  # age-25-44 60% coverage
        config["vaccination_coverage"] = 0.6
        for agent in agents:
            if agent.age >= 25 and agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")

    if scenarios == "90%_age-15-24":  # age-15-24  90% coverage
        config["vaccination_coverage"] = 0.9
        for agent in agents:
            if agent.age <= 24:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")

    if scenarios == "90%_age-25-44":  # age-25-44  90% coverage  
        config["vaccination_coverage"] = 0.9      
        for agent in agents:
            if agent.age >= 25 and agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")
            
    if scenarios == "60%_female":  #female in ages 15-44 only 60% coverage
        config["vaccination_coverage"] = 0.6        
        for agent in agents:
            if agent.gender == "female" and agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")
            
    if scenarios == "60%_female_male":  # female and male in ages 15-44 60% coverage
        config["vaccination_coverage"] = 0.6       
        for agent in agents:
            if agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")

    if scenarios == "90%_female":  # female in ages 15-44 only 90% coverage 
        config["vaccination_coverage"] = 0.9      
        for agent in agents:
            if agent.gender == "female" and agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")       

    if scenarios == "90%_female_male":  # female and male in ages 15-44  90% coverage      
        config["vaccination_coverage"] = 0.9
        for agent in agents:
            if agent.age <= 44:
                total_agents += 1
                if agent.vaccined == False:
                    non_vaccined_agents.append(agent)
                else:
                    vaccined_agents.append(agent)
        VC_constant(total_agents, non_vaccined_agents, vaccined_agents, config["vaccination_coverage"], config, scenario_type="default")

# def VC_constant(total_agents, non_vaccined_agents, vaccined_agents, coverage, config, scenario_type):
#     num_agents_to_vaccinate = int(total_agents * coverage)
    
#     if scenario_type == "scenario_2":
#         Vefficacy = config["vaccine_efficacy"]
#     else:
#         Vefficacy = config.get("vaccine_efficacy_expo", [config.get("vaccine_efficacy")])[0]

#     while len(vaccined_agents) < num_agents_to_vaccinate:
#         ## pop a non_vaccined agent from non_vaccined_agents list
#         agent = non_vaccined_agents.pop(0)
#         ## vaccinate the agent
#         agent.vaccined = True
#         agent.had_vaccine = True
#         agent.current_efficacy = Vefficacy
#         agent.vaccined_period = config['weeks']
#         ## add the agent to the vaccined_agents list
#         vaccined_agents.append(agent)
    
#     # while len(vaccined_agents) > num_agents_to_vaccinate:
#     #     agent = vaccined_agents.pop()
#     #     agent.vaccined = False
#     #     agent.current_efficacy = 0.0
#     #     non_vaccined_agents.append(agent)

def VC_constant(total_agents, non_vaccined_agents, vaccined_agents, coverage, config, scenario_type):
    target_num = int(total_agents * coverage)
    current_num = len(vaccined_agents)
    num_to_add = max(0, target_num - current_num)

    if scenario_type == "scenario_2":
        Vefficacy = config["vaccine_efficacy"]
    else:
        Vefficacy = config.get("vaccine_efficacy_expo", [config.get("vaccine_efficacy")])[0]

    for _ in range(num_to_add):
        if not non_vaccined_agents:
            break
        agent = non_vaccined_agents.pop(0)
        agent.vaccined = True
        agent.had_vaccine = True
        agent.current_efficacy = Vefficacy
        agent.vaccined_period = config['weeks']
        vaccined_agents.append(agent)

        
"""scenario 4"""
#========================scenario 4: vaccine duration =====================
def scenario_4():
    # set up parallelism
    parallelism = 7
    
    # set up configurations
    config = get_config("config.json")
    config["vaccination_coverage"] = 0.6
    config["PID_pro_CT_induced"] = 0.16

    # set up experiment parameters
    input_exp_key = "vaccine_efficacy_varying"  # experiment parameter 1 key
    input_exp_values = [
        "no_vaccine",
        "duration_of_1_years",
        "duration_of_5_years",
        "duration_of_10_years",
        "duration_of_15_years",
        "duration_of_20_years",
        "Not_changed"
    ]  # experiment parameter 1 values
    
    print(f"Parameters: {input_exp_key}:")

    exp_key_list = [input_exp_key]
    exp_value_comb_list = list(product(input_exp_values))

    # execute the simulation
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_vaccine_duration,
    )

def change_vaccine_duration(agents, config, efficacy, week):

    config["vaccine_mode"] = efficacy
    config["vaccine_mechanism"] = (
        "none" if efficacy == "no_vaccine" else "susceptibility_only"
    )
    
    if efficacy == "no_vaccine":
        for agent in agents:
            agent.vaccined = False
            agent.vaccined_period = 0

    elif efficacy == "duration_of_1_years":
        config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/1_year_decay.csv",
        delimiter=",")
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 1 years of vaccine duration 

    elif efficacy == "duration_of_5_years":
        config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/5_year_decay.csv",
        delimiter=",")
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 5 years of vaccine duration

    elif efficacy == "duration_of_10_years":
        config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/10_year_decay.csv",
        delimiter=",")
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 10 years of vaccine duration
    
    elif efficacy == "duration_of_15_years":
        config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/15_year_decay.csv",
        delimiter=",")
        for agent in agents:
            if  agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 15 years of vaccine duration

    elif efficacy == "duration_of_20_years":
        config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/20_year_decay.csv",
        delimiter=",")
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
    
    elif efficacy == "Not_changed":
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    config["vaccine_efficacy"] = 0.8
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy"]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration

#========================scenario 4: vaccine duration =====================

"""scenario 5"""
#========================scenario 5: vaccine time-varying efficacy=====================
def scenario_5():
    # set up parallelism
    parallelism = 3
    
    # save_agents_initialization(config)
    config = get_config("config.json")

    # configurations
    distribution = exponential_decay(
        x=np.arange(0, config["weeks"]+10),
        initial_value=0.8,
        decay_rate=1 / 520, # 1/520 is the decay rate for 5 years
    )
    config["vaccine_efficacy_expo"] = distribution
    np.savetxt(
        "./data_saved/time_varying_efficacy.csv",
        config["vaccine_efficacy_expo"],
        delimiter=",",
    )
    config["PID_pro_CT_induced"] = 0.16
    config["vaccination_coverage"] = 0.6

    # set up experiment parameters
    input_exp_key = "vaccine_efficacy_varying"  # experiment parameter 1 key
    input_exp_values = [
        "no_vaccine",
        "Not_changed",  ##fixed at 0.8 without change
        "time-varying",
    ]  # experiment parameter 1 values
    
    print(f"Parameters: {input_exp_key}:")

    exp_key_list = [input_exp_key]
    exp_value_comb_list = list(product(input_exp_values))

    # execute the simulation
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_vaccine_efficacy_time_varying,
    )

def change_vaccine_efficacy_time_varying(agents, config, efficacy, week):

    config["vaccine_mode"] = efficacy
    config["vaccine_mechanism"] = (
        "none" if efficacy == "no_vaccine" else "susceptibility_only"
    )

    if efficacy == "no_vaccine":
        config["vaccine_efficacy"] = 0
        for agent in agents:
            agent.vaccined = False
    
    elif efficacy == "Not_changed":
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    config["vaccine_efficacy"] = 0.8
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.current_efficacy = config["vaccine_efficacy"]
                    agent.vaccined_period = config['weeks'] # 20 years of vaccine duration
                                                      
    elif efficacy == "time-varying":
        for agent in agents:
            if agent.age <= 44 and not agent.had_vaccine:
                if random.random() < config["vaccination_coverage"]:
                    agent.vaccined = True
                    agent.had_vaccine = True
                    agent.vaccined_period = config['weeks']
                    agent.weeks_since_vaccine = 0
                    agent.current_efficacy = config["vaccine_efficacy_expo"][0]
                    
def exponential_decay(x, initial_value, decay_rate):
    return initial_value * np.exp(-decay_rate * x)
#========================scenario 5: vaccine time-varying efficacy=====================


"""scenario 6"""
#========================scenario 6: vaccine coverage scale up===================== 
def scenario_6():
    # set up parallelism
    parallelism = 5
    
    # set up configurations
    config = get_config("config.json")
    config["PID_pro_CT_induced"] = 0.16
    config["vaccine_efficacy_expo"] = np.loadtxt(
        "./data_saved/10_year_decay.csv", delimiter=","
    )
    config["use_scale_up"] = True
    config["scale_up_target"] = 0.6
    # config["vaccination_coverage"] = 0   # dummy, not used

    # set up experiment parameters

    input_exp_key = "VC_scale_up_years"
    input_exp_values = [
        "no_vaccine",
        "5_years_scale_up",
        "10_years_scale_up",
        "20_years_scale_up",
        "immediate_scale_up"
    ]
    # input_exp_values = [
    #     "10_years_scale_up",
    #     "immediate_scale_up"
    # ]
    print(f"Parameters: {input_exp_key}:")
    exp_key_list = [input_exp_key]
    exp_value_comb_list = list(product(input_exp_values))
    
    # ===== execute simulation =====
    execute_simulation(
        config=config,
        parallelism=parallelism,
        exp_key_list=exp_key_list,
        exp_value_comb_list=exp_value_comb_list,
        func=change_scale_up_years
    )
  
def change_scale_up_years(agents, config, scale_up_years, week):
    config["vaccine_mode"] = scale_up_years
    config["vaccine_mechanism"] = (
        "none" if scale_up_years == "no_vaccine" else "susceptibility_only"
    )
    
    if scale_up_years == "no_vaccine":
        config["vaccination_coverage"] = 0.0
        for agent in agents:
            agent.vaccined = False

    if scale_up_years == "5_years_scale_up":
        config["scale_up_years"] = 5
    
    if scale_up_years == "10_years_scale_up":
        config["scale_up_years"] = 10
    
    if scale_up_years == "20_years_scale_up":
        config["scale_up_years"] = 20 

    if scale_up_years == "immediate_scale_up":
        config["scale_up_years"] = 0

def scale_up_coverage(config):
    """
    Linear scale-up of vaccination coverage from 0 to target.
    """
    start = config["weeks_start_vaccine"]
    duration = config["scale_up_years"] * 52
    target = config["scale_up_target"]
    
    current_week = config.get("current_week", 0)

    if current_week < start:
        return 0.0
    elif duration == 0:
        return target
    elif current_week >= start + duration:
        return target
    else:
        return target * (current_week - start) / duration
