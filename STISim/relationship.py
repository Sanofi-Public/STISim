import numpy as np
import random
import concurrent.futures
from random import choices
from scipy.stats import truncnorm

# Revised probability function for relationship based on the age difference
def relationship_probability(age1, age2, gender1, gender2, sexual_behavior_1, sexual_behavior_2, mean_age_diff, sigma):
    """
    Calculate the relationship probability based on Gaussian distribution of age difference
    mean_age_diff: Mean age difference where positive indicates the male is older for heterosexual
    sigma: Standard deviation of the age difference.
    """

    if "FSW" in [sexual_behavior_1, sexual_behavior_2]:
        return 1

    if gender1 != gender2:  # Heterosexual relationship
        if gender1 == "male":
            age_diff = age1 - age2 - mean_age_diff
        else:
            age_diff = age2 - age1 - mean_age_diff
    else:  # Homosexual relationship without age preference
        age_diff = abs(age1 - age2)

    probability = np.exp(-0.5 * (age_diff / sigma) ** 2)
    return probability


def get_candidates(agents):
    """
    Efficiently filter agents who are eligible to form new relationships.
    """
    # use list comprehension with filtering conditions
    candidates = [
        agent for agent in agents
        if agent.dnp > len(agent.existing_partners)  # Needs more partners
        and agent.gap_time <= 0  # Eligible for new relationships
    ]

    # print(f"Number of candidates: {len(candidates)}")
    
    # Pre-group candidates by sexual behavior and gender
    male_heterosexual = [a for a in candidates if a.gender == "male" and a.sexual_behavior == "heterosexual"]
    female_heterosexual = [a for a in candidates if a.gender == "female" and a.sexual_behavior == "heterosexual"]
    
    msm = [a for a in candidates if a.sexual_behavior == "MSM"]
    fsw = [a for a in candidates if a.sexual_behavior == "FSW"]
    
    return {
        "male_heterosexual": male_heterosexual,
        "female_heterosexual": female_heterosexual,
        "msm": msm,
        "fsw": fsw,
    }


def match_partners(agents, potential_partners, config):
    """
    Efficiently match agents with potential partners based on relationship probabilities.
    """
    new_relationships = 0
    for agent in agents:
        if len(agent.existing_partners) >= agent.dnp:
            continue  # Skip if the agent does not need more partners

        # Filter potential partners who can still form relationships
        valid_partners = [
            partner for partner in potential_partners
            if len(partner.existing_partners) < partner.dnp
            and agent not in [p for p, _ in partner.existing_partners]
        ]

        if not valid_partners:
            continue

        # Calculate relationship probabilities only for valid partners
        probabilities = [
            relationship_probability(
                agent.age, partner.age,
                agent.gender, partner.gender,
                agent.sexual_behavior, partner.sexual_behavior,
                config["mean_age_diff"],
                config["sigma"]
            )
            for partner in valid_partners
        ]

        # Normalize probabilities
        total_probability = sum(probabilities)
        if total_probability > 0:
            probabilities = [p / total_probability for p in probabilities]

            # Select a partner based on weighted probabilities
            chosen_partner = choices(valid_partners, weights=probabilities, k=1)[0]

            # Determine relationship duration
            if "FSW" in [agent.sexual_behavior, chosen_partner.sexual_behavior]:
                duration = max(1, np.random.normal(config["fsw_mean_duration"], config["fsw_variance_duration"])) 
            else:
                if random.random() < config["long_term_probability"]:
                    duration = np.random.geometric(1 / config["long_term_time"])
                else:
                    duration = np.random.geometric(1 / config["short_term_time"])
                

            # Establish the relationship
            agent.existing_partners.append((chosen_partner, duration))
            chosen_partner.existing_partners.append((agent, duration))
            new_relationships += 1
            
            #lifetime partners count excluding FSWs
            if agent.sexual_behavior != "FSW" and chosen_partner.sexual_behavior != "FSW":
                agent.number_of_partners += 1
                chosen_partner.number_of_partners += 1


def form_relationships(agents, config, week):
    """
    Form relationships among agents using a more efficient approach.
    """

    # Step 1: Obtain pre-filtered candidate groups
    candidate_groups = get_candidates(agents)

    ##########debugger
    # if week % 52 == 0:     
    # total = 0   
    # for key, value in candidate_groups.items():
    #     print(f"Number of candidates in group {key}: {len(value)}")      
    #     total += len(value)      
    # print(f"Week {week}: Number of candidates: {total}")

    # if week % 52 == 0:
    #     print(f"Week {week}: Number of candidates: {total}")
    ##########debugger


    # Step 2: Define matching strategies for each group
    # Heterosexual relationships
    match_partners(
        candidate_groups['male_heterosexual'],
        candidate_groups['female_heterosexual'],
        config
    )

    # MSM relationships (male-to-male)
    match_partners(
        candidate_groups['msm'],
        candidate_groups['msm'],
        config
    )

    # FSW (female sex worker) relationships (FSW can match with anyone)
    all_potential_partners = (
        candidate_groups['male_heterosexual']
        + candidate_groups['female_heterosexual']
        + candidate_groups['msm']
    )
    match_partners(
        candidate_groups['fsw'],
        all_potential_partners,
        config
    )

def dissolve_relationships(agents, config):
    processed = set()  # record the pairs that have been processed
    for agent in agents:
        new_partners = []
        for partner, duration in agent.existing_partners:
            new_duration = duration - 1
            if new_duration > 0:
                new_partners.append((partner, new_duration))
            else:
                pair_id = tuple(sorted([id(agent), id(partner)]))
                if pair_id in processed:
                    continue
                
                if duration >= config["long_term_time"] / 2:
                    gap_time = max(52, np.random.normal(config["ttime_gap_long"], config["ttime_gap_long_variance"]))
                else:
                    gap_time = max(4, np.random.normal(config["ttime_gap_short"], config["ttime_gap_short_variance"]))
                # remove partners
                partner.existing_partners = [(p, d) for (p, d) in partner.existing_partners if p != agent]
                # time gap FSWs do not have time gap
                if "FSW" in [agent.sexual_behavior, partner.sexual_behavior]:
                    agent.gap_time = 0
                    partner.gap_time = 0
                else:
                    agent.gap_time = gap_time
                    partner.gap_time = gap_time
                processed.add(pair_id)
        agent.existing_partners = new_partners


#===================================below is disease transmission in the network ===================================
def infection_occurs_in_relationships(batch, config, current_week):
    for agent in batch:
        for partner, _ in agent.existing_partners:
            # Infection occurs
            if (agent.state in ["I", "E"] and agent.infectious_period >= 0) or (
                partner.state in ["I", "E"] and partner.infectious_period >= 0
                ):
                if agent.state in ["I", "E"]:
                   infector = agent
                   infectee = partner
                else:
                    infector = partner
                    infectee = agent
                # determining the transmission probability
                NNL = config["n_weekly_contacts_longterm"]
                NNS = config["n_weekly_contacts_shorterm"]
                NNFSW = config["n_weekly_contacts_FSW"]
                ppc_female = config["infection_probability_per_contact_female"]
                ppc_male = config["transmission_probability_reduced_male"] * ppc_female

                if infectee.age > 24:
                    ppc_female = ppc_female * config["transmission_probability_reduced_older"]
                    ppc_male = ppc_male * config["transmission_probability_reduced_older"]  
   
                if "FSW" in [infector.sexual_behavior, infectee.sexual_behavior]:
                    N = NNFSW
                elif random.random() < config["long_term_probability"]:
                    N = NNL
                else:
                    N = NNS

                P_female_to_male = 1 - (1 - ppc_male) ** N
                P_male_to_female = 1 - (1 - ppc_female) ** N
                P_male_to_male = 1 - (1 - ppc_male) ** N

                if infector.gender == "female":
                    transmission_probability = P_female_to_male
                elif infector.gender == "male":
                    if infector.sexual_behavior == "MSM":
                        transmission_probability = P_male_to_male
                    else:
                        transmission_probability = P_male_to_female
                
                #========================================uncomment only for scenario_1========================================
                infectee_factor = 1.0
                infector_factor = 1.0
                mechanism = config["vaccine_mechanism"]

                if mechanism == "susceptibility_only":
                    infectee_factor = 1 - infectee.current_efficacy  if infectee.vaccined else 1
                elif mechanism == "infectiousness_only":
                    infector_factor = 1 - infector.current_efficacy if infector.vaccined else 1
                elif mechanism == "both":
                    if infectee.vaccined:
                        infectee_factor = 1 - infectee.current_efficacy
                    if infector.vaccined:
                        infector_factor = 1 - infector.current_efficacy
                
                tp = transmission_probability * infectee_factor * infector_factor
                #========================================uncomment only for scenario_1========================================

                
                #========================================uncomment for the remining scenarios==============================
                # infectee_factor = 1- infectee.current_efficacy if infectee.vaccined else 1
                # infector_factor = 1- infector.current_efficacy if infector.vaccined else 1
                
                # tp = transmission_probability * infectee_factor 
                #========================================uncomment for the remining scenarios==============================
                # print(f"Transmission probability: {tp}")
                if random.random() < tp:
                    new_state = (
                        "E" if random.random() < config["asymptomatic_fraction"] else "I"
                    )
                    process_agent_state(agent=infectee, new_state=new_state, config=config, current_week = current_week)

def process_agent_state(agent, new_state, config, current_week):
    if agent.state == "R":
        if random.random() < (1 - agent.immunity):
            update_infection_state(agent, new_state, config, current_week)

    elif agent.state == "S":
        update_infection_state(agent, new_state, config, current_week)

def update_infection_state(agent, new_state, config, current_week):
    agent.state = new_state
    agent.infectious_period = -2
    agent.CT_episodes_count += 1

    weekly_seek_treatment_probability = config["seek_treatment_probability_male"] if agent.gender == "male" else config["seek_treatment_probability_female"]
    # agent become Symptomatic status after infection then give some attributes to this agent
    # about treatment 

    if new_state == "I":  
        # probability to seek treatment
        if random.random() < weekly_seek_treatment_probability:
            agent.seeks_treatment = True
            agent.weeks_until_treatment = max(1, np.random.normal(config["clearance_duration_treatment_mean"], config["clearance_duration_treatment_variance"]))
            agent.had_treated_CT = True
            agent.PID_risk_untreated = 0  # reset the PID risk if treated
        else:
            agent.seeks_treatment = False   
            agent.sick_period = max(45, np.random.normal(config["clearance_duration_natural_mean"], config["clearance_duration_natural_variance"])) 
            TT = agent.sick_period
            agent.PID_risk_untreated = 1 - (1 - config["PID_pro_CT_induced"]) ** (1 / TT)
                     
    #about screening and detection
    else: 
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
                    agent.PID_risk_untreated = 0  # reset the PID risk if treated
        else:
            agent.seeks_treatment = False   
            agent.sick_period = max(45, np.random.normal(config["clearance_duration_natural_mean"], config["clearance_duration_natural_variance"])) 
            TT = agent.sick_period
            agent.PID_risk_untreated = 1 - (1 - config["PID_pro_CT_induced"]) ** (1 / TT)
    

