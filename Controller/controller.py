import simpy
import random
import statistics
import pandas as pd
import itertools
import contextlib
import os

from Model.boat import Boat
from Model.cargo import Cargo
from Model.cargo_optimizer import load_optimal_cargo


# --- Utility Functions for Random Generation ---
def random_boat():
    """
    Create a Boat with randomized max_weight and max_space using an exponential distribution.
    Mean weight capacity is ~10000 units and mean space capacity is ~500 units.
    """
    max_weight = max(1000, int(random.expovariate(1 / 10000)))  # ensuring a minimum capacity
    max_space = max(100, int(random.expovariate(1 / 500)))  # ensuring a minimum capacity
    name = "Boat_" + str(random.randint(1, 1000))
    return Boat(name, max_weight, max_space)


def random_cargo():
    """
    Create a Cargo with randomized weight, space_required, and value_per_unit using an exponential distribution.
    Mean weight ~2000 units, mean space ~150 units, mean value ~100.
    """
    weight = max(100, int(random.expovariate(1 / 2000)))  # ensure non-zero weight
    space_required = max(50, int(random.expovariate(1 / 150)))  # ensure non-zero space requirement
    value_per_unit = max(10, random.expovariate(1 / 100))  # ensure non-zero value per unit
    name = "Cargo_" + str(random.randint(1, 1000))
    category = random.choice(["Container", "Bulk", "Liquid", "Refrigerated", "Luxury"])
    return Cargo(name, value_per_unit, weight, space_required, category)


# --- Canal Simulation Class ---
class CanalSimulation:
    def __init__(self, env, num_locks, avg_service_time, base_fee=1000):
        self.env = env
        self.lock = simpy.Resource(env, capacity=num_locks)
        self.avg_service_time = avg_service_time  # average service time in the canal
        self.base_fee = base_fee  # base fee when no waiting occurs
        self.ship_logs = []  # log for ship events
        self.cargo_logs = []  # log for cargo details (per ship)
        self.canal_logs = []  # log for overall canal stats
        self.total_fees_collected = 0
        self.ship_count = 0
        self.wait_times = []  # for computing average wait time

    def process_ship_with_cargo(self, ship, cargo_options):
        """
        Process a ship:
          - The ship arrives.
          - Its cargo is optimized and loaded.
          - It requests access to the canal locks.
          - Once granted, wait time is measured and a fee is computed.
          - The ship undergoes service before exiting.
          - All events are logged.
        """
        arrival_time = self.env.now

        # Suppress optimizer's extra logs using contextlib.redirect_stdout
        with contextlib.redirect_stdout(None):
            load_optimal_cargo(ship, cargo_options)

        with self.lock.request() as request:
            yield request
            entry_time = self.env.now
            wait_time = entry_time - arrival_time
            self.wait_times.append(wait_time)
            fee = self.base_fee / (1 + wait_time)
            self.total_fees_collected += fee

            service_time = random.expovariate(1.0 / self.avg_service_time)
            yield self.env.timeout(service_time)
            exit_time = self.env.now

            cargo_value = sum(c.value_per_unit * c.weight for c in ship.cargo_list)
            self.ship_logs.append({
                "Ship": ship.name,
                "Arrival": arrival_time,
                "Entry": entry_time,
                "Wait Time": wait_time,
                "Service Time": service_time,
                "Exit": exit_time,
                "Fee": fee,
                "Cargo Value": cargo_value,
                "Cargo Weight": ship.current_weight,
                "Cargo Space": ship.current_space,
                "Free Weight": ship.max_weight - ship.current_weight,
                "Free Space": ship.max_space - ship.current_space
            })
            for cargo in ship.cargo_list:
                self.cargo_logs.append({
                    "Ship": ship.name,
                    "Cargo": cargo.name,
                    "Category": cargo.category,
                    "Weight": cargo.weight,
                    "Space": cargo.space_required,
                    "Value": cargo.value_per_unit * cargo.weight
                })
            self.ship_count += 1

    def run(self, until, arrival_rate, cargo_options):
        """
        Starts the ship arrivals process and runs the simulation until the given time.
        """

        def ship_arrivals(env, arrival_rate, canal_sim, cargo_options):
            while True:
                interarrival = random.expovariate(arrival_rate)
                yield env.timeout(interarrival)
                ship = random_boat()
                env.process(canal_sim.process_ship_with_cargo(ship, cargo_options))

        self.env.process(ship_arrivals(self.env, arrival_rate, self, cargo_options))
        self.env.run(until=until)
        average_wait = statistics.mean(self.wait_times) if self.wait_times else 0
        self.canal_logs.append({
            "Total Ships": self.ship_count,
            "Average Wait Time": average_wait,
            "Total Fees Collected": self.total_fees_collected,
            "Simulation Time": until
        })


# --- Simulation Runner Function ---
def run_simulation(simulation_time, arrival_rate, avg_service_time, num_locks, cargo_options):
    random.seed(42)  # For reproducibility
    env = simpy.Environment()
    canal_sim = CanalSimulation(env, num_locks, avg_service_time)
    canal_sim.run(until=simulation_time, arrival_rate=arrival_rate, cargo_options=cargo_options)
    df_ships = pd.DataFrame(canal_sim.ship_logs)
    df_cargos = pd.DataFrame(canal_sim.cargo_logs)
    df_canal = pd.DataFrame(canal_sim.canal_logs)
    return df_ships, df_cargos, df_canal


def run_all_scenarios():
    simulation_time = 1000  # Total simulation time

    # Define ranges for parameters
    arrival_rate_options = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    avg_service_time_options = [2.5, 5, 7.5, 10]
    num_locks_options = [1, 2, 3, 4, 5]

    # Create a global list of cargo options (10 random cargo types)
    cargo_options = [random_cargo() for _ in range(10)]

    # Generate scenario combinations using itertools.product
    scenarios = list(itertools.product(arrival_rate_options, avg_service_time_options, num_locks_options))

    master_ship_logs = []
    master_cargo_logs = []
    master_canal_logs = []

    for idx, (arrival_rate, avg_service_time, num_locks) in enumerate(scenarios, start=1):
        scenario_name = f"Scenario {idx}/{len(scenarios)}: AR={arrival_rate}, ST={avg_service_time}, Locks={num_locks}"
        print("=" * 50)
        print(f"Running {scenario_name}")
        print("=" * 50)
        df_ships, df_cargos, df_canal = run_simulation(
            simulation_time,
            arrival_rate,
            avg_service_time,
            num_locks,
            cargo_options
        )
        df_ships["Scenario"] = scenario_name
        df_cargos["Scenario"] = scenario_name
        df_canal["Scenario"] = scenario_name

        master_ship_logs.append(df_ships)
        master_cargo_logs.append(df_cargos)
        master_canal_logs.append(df_canal)

        print(f"Finished {scenario_name}\n")

    final_ships_df = pd.concat(master_ship_logs, ignore_index=True)
    final_cargos_df = pd.concat(master_cargo_logs, ignore_index=True)
    final_canal_df = pd.concat(master_canal_logs, ignore_index=True)

    ship_stats = final_ships_df.groupby("Scenario").agg(
        Total_Ships=('Ship', 'count'),
        Min_Wait_Time=('Wait Time', 'min'),
        Q1_Wait_Time=('Wait Time', lambda x: x.quantile(0.25)),
        Median_Wait_Time=('Wait Time', 'median'),
        Q3_Wait_Time=('Wait Time', lambda x: x.quantile(0.75)),
        Max_Wait_Time=('Wait Time', 'max'),
        Avg_Wait_Time=('Wait Time', 'mean'),
        Min_Service_Time=('Service Time', 'min'),
        Median_Service_Time=('Service Time', 'median'),
        Max_Service_Time=('Service Time', 'max'),
        Avg_Service_Time=('Service Time', 'mean'),
        Min_Fee=('Fee', 'min'),
        Median_Fee=('Fee', 'median'),
        Max_Fee=('Fee', 'max'),
        Avg_Fee=('Fee', 'mean'),
        Total_Fees=('Fee', 'sum'),
        Avg_Cargo_Value=('Cargo Value', 'mean'),
        Min_Cargo_Value=('Cargo Value', 'min'),
        Max_Cargo_Value=('Cargo Value', 'max')
    ).reset_index()

    return final_ships_df, final_cargos_df, final_canal_df, ship_stats


if __name__ == "__main__":
    final_ships_df, final_cargos_df, final_canal_df, ship_stats = run_all_scenarios()

    # --- Export CSV Files to the View Folder ---
    # Determine output directory relative to this file's location (assuming this file is in Controller and View is at ../View)
    output_dir = os.path.join(os.path.dirname(__file__), "..", "View")
    os.makedirs(output_dir, exist_ok=True)

    final_ships_df.to_csv(os.path.join(output_dir, "ship_log.csv"), index=False)
    final_cargos_df.to_csv(os.path.join(output_dir, "cargo_log.csv"), index=False)
    final_canal_df.to_csv(os.path.join(output_dir, "canal_log.csv"), index=False)
    ship_stats.to_csv(os.path.join(output_dir, "ship_stats.csv"), index=False)

    print("CSV files have been generated in the View folder.")
