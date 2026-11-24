import time
from vaccine_scenarios import scenario_1, scenario_2, scenario_3, scenario_4, scenario_5, scenario_6

def main():
    scenario_1()
    
if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.6f} seconds")
