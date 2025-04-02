import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

import os


def load_and_describe():
    # Define file names
    ship_log_file = "ship_log.csv"
    cargo_log_file = "cargo_log.csv"
    canal_log_file = "canal_log.csv"
    ship_stats_file = "ship_stats.csv"

    # Check if CSV files exist
    missing_files = []
    for file in [ship_log_file, cargo_log_file, canal_log_file, ship_stats_file]:
        if not os.path.exists(file):
            missing_files.append(file)
    if missing_files:
        print("The following CSV files were not found. Please run the simulation first:")
        for f in missing_files:
            print("  ", f)
        return

    # Load the CSV files into DataFrames
    df_ships = pd.read_csv(ship_log_file)
    df_cargos = pd.read_csv(cargo_log_file)
    df_canal = pd.read_csv(canal_log_file)
    ship_stats = pd.read_csv(ship_stats_file)

    # Print descriptive statistics for each DataFrame
    print("Ship Log Description:")
    print(df_ships.describe(include='all'))

    print("\nCargo Log Description:")
    print(df_cargos.describe(include='all'))

    print("\nCanal Log Description:")
    print(df_canal.describe(include='all'))

    print("\nShip Statistics Description:")
    print(ship_stats.describe(include='all'))


if __name__ == "__main__":
    load_and_describe()
