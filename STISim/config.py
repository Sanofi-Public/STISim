import ast
import json


def read_config(file_path):
    with open(file_path, "r") as f:
        config = json.load(f)
    return config


def parse_keys(d):
    parsed_dict = {}
    for key, value in d.items():
        parsed_key = ast.literal_eval(key)
        parsed_dict[parsed_key] = value
    return parsed_dict


def parse_config(config):
    config["initial_infected_fraction_groups"]["female_initial_infected"] = parse_keys(
        config["initial_infected_fraction_groups"]["female_initial_infected"]
    )
    config["initial_infected_fraction_groups"]["male_initial_infected"] = parse_keys(
        config["initial_infected_fraction_groups"]["male_initial_infected"]
    )
    config["male_age_groups"] = parse_keys(config["male_age_groups"])
    config["female_age_groups"] = parse_keys(config["female_age_groups"])
    config["immunity_recovered"] = parse_keys(config["immunity_recovered"])
    config["screen_pro_male"] = parse_keys(config["screen_pro_male"])
    config["screen_pro_female"] = parse_keys(config["screen_pro_female"])
    #config["PID_probability"] = parse_keys(config["PID_probability"])   
    return config

def get_config(file_path):
    return parse_config(read_config(file_path))
