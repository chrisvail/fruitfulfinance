from time import perf_counter
import yaml
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import multiprocessing as mp
from factory import Simulation
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
        if "uncertainty" not in file: continue
        stream = open("configs/" + file, 'r')
        dictionary = yaml.safe_load(stream)

        path = os.path.abspath(".")
        if not os.path.isdir(f"{dictionary['name']}"):
            os.mkdir(path + f"\\{dictionary['name']}")

        tasks = ((dictionary, i) for i in range(dictionary["runs"]))
        t0 = perf_counter()
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results = pool.starmap(worker, tasks)

        print(f"Completed {dictionary['runs']} runs in {perf_counter() - t0} seconds")
        results = [x.to_numpy() for x in results]
        results = np.stack(results, axis=-1)
        np.save(f"{dictionary['name']}/{dictionary['name']}_all.npy", results)
        np.save(f"Results/{dictionary['name']}_all.npy", results)


def worker(config, run_no):
    sim = Simulation(config["sim_details"], config["steps"])
    sim.run()
    df = pd.DataFrame(sim.record)
    df.to_csv(f"{config['name']}/{config['name']}{run_no}.csv")
    return df


if __name__ == '__main__':
    main()