from time import perf_counter
import yaml
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import multiprocessing as mp
from actionfunction import ActionFunction

from factory import Simulation, Client, Distribution
import os

def main():

    files = [
        "configs/deterministic.yaml",
        "configs/customer_uncertainty.yaml",
        "configs/location_uncertainty.yaml",
        "configs/misc_uncertainty.yaml",
        "configs/uncertainty_total_base.yaml",
    ]

    for file in tuple(os.walk("./configs"))[0][2]:
        Client.client_churned = 0
        Client.client_count = 0
        if "uncertainty" not in file and "real_option" not in file: continue
        stream = open("configs/" + file, 'r')
        dictionary = yaml.safe_load(stream)

        path = os.path.abspath(".")
        if not os.path.isdir(f"{dictionary['name']}"):
            os.mkdir(path + f"\\{dictionary['name']}")

        # tasks = ((dictionary, i) for i in range(dictionary["runs"]))
        results_total = None
        t0 = perf_counter()
        print(f"Starting to run: {dictionary['name']}")
        for i in range(0, dictionary["runs"], 20):
            tasks = ((dictionary, i) for i in range(i, i+20))

            with mp.Pool(processes=mp.cpu_count()) as pool:
                results = pool.starmap(worker, tasks)

            print(f"\tCompleted {i+20} runs in {perf_counter() - t0} seconds")
            results = [x.to_numpy() for x in results]
            results = np.stack(results, axis=-1)

            if results_total is None:
                results_total = results
            else:
                results_total = np.concatenate((results_total, results), axis=2)

        np.save(f"{dictionary['name']}/{dictionary['name']}_all.npy", results_total)
        np.save(f"Results/{dictionary['name']}_all.npy", results_total)


def main2():

    file = "uncertainty_cs1.yaml"

    stream = open("configs/" + file, 'r')
    dictionary = yaml.safe_load(stream)

    path = os.path.abspath(".")
    if not os.path.isdir(f"{dictionary['name']}"):
        os.mkdir(path + f"\\{dictionary['name']}")

    print(f"Name: {dictionary['name']}")
    print(f"Runs: {dictionary['runs']}")

    tasks = tuple((dictionary, i) for i in range(dictionary["runs"]))
    print(f"Task Length: {len(tasks)}")
    t0 = perf_counter()
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.starmap(worker, tasks)

    print(f"Completed {dictionary['runs']} runs in {perf_counter() - t0} seconds")
    results = [x.to_numpy() for x in results]
    results = np.stack(results, axis=-1)
    np.save(f"{dictionary['name']}/{dictionary['name']}_all.npy", results)
    np.save(f"Results/{dictionary['name']}_all.npy", results)


def worker(config, run_no):

    sim_details: dict = config["sim_details"]

    if "customer_change" in sim_details.keys() and "build_change" in sim_details.keys():
        action_function = ActionFunction(sim_details["customer_change"], sim_details["build_change"])
    else:
        action_function = None

    sim = Simulation(config["sim_details"], config["steps"], action_function)
    sim.run()
    df = pd.DataFrame(sim.record)
    # df.to_csv(f"{config['name']}/{config['name']}_{run_no}.csv")
    return df


if __name__ == '__main__':
    main()