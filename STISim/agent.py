import numpy as np
import random
import concurrent.futures
import copy
from scipy.stats import truncnorm

class Agent:

    _id_counter = 1

    def __init__(
        self,
        gender,
        age,
        age_group,
        sexual_behavior,
        dnp,
        preferred_duration = 0,
        state="S",
        gap_time=0,
        immunity=0,
        existing_partners=None,
        sick_period=0,
        weeks_until_treatment=0,
        infectious_period=0,
        recovery_period=0,
        vaccined=False,  # track if the agent has been vaccinated
        vaccined_period=0,  # track the duration of the vaccination period
        seeks_treatment=False,  # track if the symptomatic agent seeks treatment
        screened=False,  # track if the asymptomatic agent has been screened
        detected=False,  # track if the screened agent has been dectected
        PID_risk_untreated = 0, #track the risk of PID if the agent is untreated

        CT_episodes_count = 0,
        PID = False,
        PID_onset_age = None,
        PID_onset_week = None,

        had_treated_CT=False,#track if the agent has ever been treated for CT
        had_vaccine = False,
        weeks_since_vaccine = 0,

        number_of_partners=0,  # track the lifetime number of partners
        PID_episodes_count=0,
        PID_from_CT=False, #track if the PID is from CT infection
        current_efficacy = 0,
    ):
        self.id = Agent._id_counter
        Agent._id_counter += 1 #track agent id from the max id in the loaded simulation
        if existing_partners is None:
            existing_partners = []
        self.gender = gender
        self.age = age
        self.age_group = age_group
        self.sexual_behavior = sexual_behavior
        self.dnp = dnp
        self.preferred_duration = preferred_duration
        self.state = state
        self.gap_time = (
            gap_time  # Time during which the agent cannot form new partnerships
        )
        # new attributes for the case with CT
        self.immunity = immunity
        self.existing_partners = existing_partners
        self.sick_period = sick_period  # duration of infection state
        self.infectious_period = infectious_period  # counter for the infectious period
        self.recovery_period = recovery_period
        self.vaccined = vaccined
        self.vaccined_period = vaccined_period
        self.weeks_until_treatment = weeks_until_treatment
        self.seeks_treatment = seeks_treatment
        self.screened = screened
        self.detected = detected

        self.CT_episodes_count = CT_episodes_count
        self.PID = PID
        self.PID_onset_age = PID_onset_age
        self.PID_onset_week = PID_onset_week
        self.PID_from_CT = PID_from_CT
        self.PID_risk_untreated = PID_risk_untreated

        self.had_treated_CT = had_treated_CT
        self.had_vaccine = had_vaccine
        self.weeks_since_vaccine = weeks_since_vaccine
        self.number_of_partners = number_of_partners
        self.PID_episodes_count = PID_episodes_count
        self.current_efficacy = current_efficacy

# parallel initialization
def batch_init(config, current_week):
    agents = []

    num_agents = config["num_agents"]
    dnp_choices = [1, 2, 3]
    dnp_weights = [
        1 - config["cheating_rate"],
        config["cheating_rate"] * config["two_dnps_rate"],
        config["cheating_rate"] * config["three_dnps_rate"]
    ]

    for i in range(num_agents):
        # Ensure a 1:1 gender ratio
        gender = "male" if random.random() < config["ratio_male_female"] else "female"

        #age-distribution based on gender; hetergoenous population of female sex workers; MSM; heterosexual agents
        # age; age_group; sexual_behavior
        if gender == "male":
            age_group_choices = list(config["male_age_groups"].keys())
            age_group_weights = list(config["male_age_groups"].values())
            if random.random() < config["MSM_rate"]:
                sexual_behavior = "MSM"
            else:
                sexual_behavior = "heterosexual"
        else:
            age_group_choices = list(config["female_age_groups"].keys())
            age_group_weights = list(config["female_age_groups"].values())
            if random.random() < config["FSW_rate"]:
                sexual_behavior = "FSW"
            else:
                sexual_behavior = "heterosexual"
        
        age_group = random.choices(age_group_choices, weights=age_group_weights, k=1)[0]
        age = random.uniform(age_group[0], age_group[1])
        
        # dnp; preferred_duration
        if sexual_behavior == "FSW":
            dnp = max(3, int(np.random.normal(config["fsw_mean_dnp"], config["fsw_variance_dnp"])))   
        else:
            dnp = random.choices(dnp_choices, dnp_weights, k=1)[0]
             
        new_agent = Agent(
            gender=gender,
            age=age,
            age_group=age_group,
            sexual_behavior=sexual_behavior,
            dnp=dnp
        )

        # initialize the agent infection state
        init_infection_state(
            agent=new_agent,
            config=config,
            week = current_week
        )
        agents.append(new_agent)
    
    return agents

def PID_development(agent, config, current_week):
    # =========================
    # 1. Baseline all-cause PID risk
    # =========================
    PID_pro = config["PID_probability"][agent.age_group]

    if random.random() < PID_pro:
        agent.PID = True
        agent.PID_from_CT = False  
        agent.PID_episodes_count += 1

        if agent.PID_onset_week is None:
            agent.PID_onset_week = current_week
        if agent.PID_onset_age is None:
            agent.PID_onset_age = agent.age

    # =========================
    # 2. Treated CT infections (multiplier risk)
    # =========================
    if agent.state in ["E", "I", "R"] and agent.seeks_treatment:
        CT_PID_pro = config["PID_probability"][agent.age_group]

        if agent.age < 41 and agent.CT_episodes_count == 1:
            CT_PID_pro *= config["CT_infected_PID_increase"]
        elif agent.age < 41 and agent.CT_episodes_count == 2:
            CT_PID_pro *= config["CT_infected_PID_increase"] * config["reinfection_PID_increase"]
        elif agent.age < 41 and agent.CT_episodes_count >= 3:
            CT_PID_pro *= config["CT_infected_PID_increase"] * config["thirdinfection_PID_increase"]

        if random.random() < CT_PID_pro:
            agent.PID = True
            agent.PID_from_CT = True  
            agent.PID_episodes_count += 1

            if agent.PID_onset_week is None:
                agent.PID_onset_week = current_week
            if agent.PID_onset_age is None:
                agent.PID_onset_age = agent.age

    # =========================
    # 3. Untreated CT infections (weekly hazard from infection duration)
    # =========================
       
    if agent.state in ["E", "I", "R"] and not agent.seeks_treatment: 
        if agent.CT_episodes_count > 1:
            return
        
        if random.random() < agent.PID_risk_untreated:
            agent.PID = True
            agent.PID_from_CT = True
            agent.PID_episodes_count += 1
            
            if agent.PID_onset_week is None:
                agent.PID_onset_week = current_week
            if agent.PID_onset_age is None:
                agent.PID_onset_age = agent.age

# initialize the agent infection state
def init_infection_state(agent, config, week):

    if agent.gender == "male":
        initial_infected_fraction = config["initial_infected_fraction_groups"]["male_initial_infected"][agent.age_group]
        weekly_seek_treatment_probability = config["seek_treatment_probability_male"]
    else:
        initial_infected_fraction = config["initial_infected_fraction_groups"]["female_initial_infected"][agent.age_group]
        weekly_seek_treatment_probability = config["seek_treatment_probability_female"]
    
    if random.random() < initial_infected_fraction:
        agent.state = "E" if random.random() < config["asymptomatic_fraction"] else "I"
        agent.CT_episodes_count += 1

        if agent.state == "I":
            if random.random() < weekly_seek_treatment_probability:
                agent.seeks_treatment = True
                agent.had_treated_CT = True
                agent.weeks_until_treatment = max(1, np.random.normal(config["clearance_duration_treatment_mean"], config["clearance_duration_treatment_variance"]))
            else:
                agent.sick_period = max(45, np.random.normal(config["clearance_duration_natural_mean"], config["clearance_duration_natural_variance"]))  # I no treatment sick duration no treatment
                TT = agent.sick_period
                agent.PID_risk_untreated = 1 - (1 - config["PID_pro_CT_induced"]) ** (1 / TT)

        else:
            screening_probability = (
                config["screen_pro_male"][agent.age_group]
                if agent.gender == "male"
                else config["screen_pro_female"][agent.age_group]
            )
            if random.random() < screening_probability:
                agent.screened = True
                # dectection
                if random.random() < config["detection_probability"]:
                    agent.detected = True
                    agent.seeks_treatment = True
                    agent.had_treated_CT = True
                    agent.weeks_until_treatment = max(1, np.random.normal(config["clearance_duration_treatment_mean"], config["clearance_duration_treatment_variance"]))
            else:
                agent.sick_period = max(45, np.random.normal(config["clearance_duration_natural_mean"], config["clearance_duration_natural_variance"]))
                TT = agent.sick_period
                agent.PID_risk_untreated = 1 - (1 - config["PID_pro_CT_induced"]) ** (1 / TT)

    if agent.gender == "female":
        PID_development(agent, config, current_week=week)

def initialize_agents_parallel(config, current_week=0, num_batch=6):
    agents = []

    num_per_batch = config["num_agents"] // num_batch
    remaining_agents = config["num_agents"] % num_batch

    # create the list with num_per_batch for all batches
    num_agents_list = [num_per_batch] * num_batch

    # distribute the remaining agents to the last batch
    num_agents_list[-1] += remaining_agents

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for num_agents in num_agents_list:
            batch_config = copy.deepcopy(config)
            batch_config["num_agents"] = num_agents
            futures.append(executor.submit(batch_init, batch_config, current_week))

    for future in concurrent.futures.as_completed(futures):
        agents.extend(future.result())
    return agents

#remove agents with age above 54 years and introduce new agents at 15 years old
def age_and_replace_agents(agents, config, current_week):
    
    new_agents = []
    male_count = sum(agent.gender == "male" for agent in agents)
    female_count = sum(agent.gender == "female" for agent in agents)
    dnp_choices = [1, 2, 3]
    dnp_weights = [
        1 - config["cheating_rate"],
        config["cheating_rate"] * config["two_dnps_rate"],
        config["cheating_rate"] * config["three_dnps_rate"]
    ]

    for agent in agents:
        if agent.age > 54:
            #dissovle relationships with partners
            for partner, _ in agent.existing_partners:
                partner.existing_partners = [
                    (p, d) for (p, d) in partner.existing_partners if p != agent
                ]

            ##new agent    
            #assign gender and sexual behavior
            if male_count > female_count:
                gender = "female"
                sexual_behavior = "FSW" if random.random() < config["FSW_rate"] else "heterosexual" 
            else:
                gender = "male"
                sexual_behavior = "MSM" if random.random() < config["MSM_rate"] else "heterosexual"   
            ##assign age and age group
            age = 15 + random.random()
            age_group = (15, 19)
            
            # dnp
            if sexual_behavior == "FSW":
                dnp = max(3, int(np.random.normal(config["fsw_mean_dnp"], config["fsw_variance_dnp"])))
            else:
                dnp = random.choices(dnp_choices, dnp_weights, k=1)[0]
            
            vaccine = False
            had_vaccine = False
            current_efficacy = 0
            vaccined_period = 0
                
            new_agent = Agent(
                gender=gender,
                age=age,
                age_group=age_group,
                sexual_behavior=sexual_behavior,
                dnp=dnp,
                state="S",
                immunity=0,
                existing_partners=[],
                sick_period=0,
                weeks_until_treatment=0,
                infectious_period=0,
                recovery_period=0,
                seeks_treatment=False,
                screened=False,
                detected=False,
                CT_episodes_count=0,
                PID=False,
                PID_onset_age=None,
                had_treated_CT=False,
                vaccined = vaccine,
                had_vaccine = had_vaccine,
                vaccined_period = vaccined_period,
                current_efficacy = current_efficacy 
            )
            new_agents.append(new_agent)
        else: 
            new_agents.append(agent)

    return new_agents

#weekly update agent infection states
def update_agent_states(agents, config, week):
    for agent in agents:
    
        agent.gap_time -= 1
        agent.infectious_period += 1

        if agent.gender == "female":
            PID_development(agent, config, current_week=week)

        if agent.vaccined:
            if agent.vaccined_period > 0:
                agent.vaccined_period -= 1
                agent.weeks_since_vaccine += 1
                if config["vaccine_mode"] == "Not_changed":
                    agent.current_efficacy = agent.current_efficacy
                else:
                    idx = agent.weeks_since_vaccine
                    agent.current_efficacy = config["vaccine_efficacy_expo"][idx]

            if agent.vaccined_period <= 0:
                agent.vaccined = False
                agent.vaccined_period = 0
                agent.weeks_since_vaccine = 0
                agent.current_efficacy = 0

        # update symptomatic agents weekly
        weekly_seek_treatment_probability = (
            config["seek_treatment_probability_male"]
            if agent.gender == "male"
            else config["seek_treatment_probability_female"]
        )
        
        if agent.state == "I": 
            
            if agent.seeks_treatment:
                agent.weeks_until_treatment -=1
                if agent.weeks_until_treatment <= 0:
                    agent.state = "R"
                    agent.immunity = config["immunity_recovered"][agent.age_group]
                    agent.recovery_period = random.uniform(0, 2*config["mean_duration_immunity_treatment"]) # obtain immunity after treatment 
                    agent.PID_risk_untreated = 0  # reset the PID risk after treatment
            #not treatment but recover naturally
            else: 
                agent.sick_period -=1
                if agent.sick_period <= 0: 
                    agent.state = "R"
                    agent.immunity = config["immunity_recovered"][agent.age_group]
                    agent.recovery_period = random.uniform(0, 2*config["mean_duration_immunity_natural"])  # obtain immunity natural recover
                    agent.PID_risk_untreated = 0  # reset the PID risk after natural recovery

            if random.random() < weekly_seek_treatment_probability:
                agent.seeks_treatment = True
                agent.had_treated_CT = True
                agent.weeks_until_treatment = max(1, np.random.normal(config["clearance_duration_treatment_mean"], config["clearance_duration_treatment_variance"]))
        
        elif agent.state == "E":
             
            if agent.screened and agent.detected: 
                    agent.weeks_until_treatment -=1
                    if  agent.weeks_until_treatment <= 0:
                        agent.state = "R"
                        agent.immunity = config["immunity_recovered"][agent.age_group]
                        agent.recovery_period = random.uniform(0, 2*config["mean_duration_immunity_treatment"]) # obtain immunity after treatment
                        agent.PID_risk_untreated = 0  # reset the PID risk after treatment
            
            else: #not screened
                agent.sick_period -= 1
                if agent.sick_period <= 0:
                    agent.state = "R"
                    agent.immunity = config["immunity_recovered"][agent.age_group]
                    agent.recovery_period = random.uniform(0, 2*config["mean_duration_immunity_natural"])  # obtain immunity natural recover
                    agent.PID_risk_untreated = 0  # reset the PID risk after natural recovery
            screening_probability = (
                config["screen_pro_male"][agent.age_group]
                if agent.gender == "male"
                else config["screen_pro_female"][agent.age_group]
                ) 
            if random.random() < screening_probability:
                    agent.screened = True
                    #dectection
                    if random.random() < config["detection_probability"]:
                        agent.detected = True
                        agent.seeks_treatment = True
                        agent.had_treated_CT = True
                        agent.weeks_until_treatment = max(1, np.random.normal(config["clearance_duration_treatment_mean"], config["clearance_duration_treatment_variance"]))

        elif agent.state == "R": 
            agent.recovery_period -= 1
            if agent.recovery_period <= 0:
                agent.state = "S"
                agent.seeks_treatment = False
                agent.screened = False
                agent.detected = False
                agent.sick_period = 0
                agent.weeks_until_treatment = 0
                agent.infectious_period = 0
                agent.immunity = 0
