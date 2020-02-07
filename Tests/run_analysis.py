import os
import sys
from multiprocessing import Pool

import numpy as np

from src.analysis.analysis import GlobalAnalysis, SimulationAnalysis





# Read the number of cores to use from the command line.
if len(sys.argv) == 2:
    NUM_PROCESS = int(sys.argv[1])
else:
    NUM_PROCESS = 1


def get_attributes_results(path):
    """Given a path were the HDF5 files from simulations are stored, 
    returns a tuple with the attributes needed for the object SimulationAnalysis
    to be built.  """
    filepath = [f for f in os.listdir(path) if f[-5:] == ".hdf5"]
    attributes = []
    for f in filepath:
        config = f[0:-5].split("#")
        config.append(path + "/" + str(f))
        attributes.append(tuple(config))

    return attributes



def analize_simulation(attr):
    return SimulationAnalysis(*attr)


# Compute the attributes of th different simulations in the results folder.
attrs = get_attributes_results("results")

# Analize each simulation creating a list os SimulationAnalysis objects
if NUM_PROCESS == 1:
    sim_analysis = [analize_simulation(attr) for attr in attrs]

else:
    pool = Pool(NUM_PROCESS)
    sim_analysis = pool.map_async(analize_simulation, attrs)
    sim_analysis = sim_analysis.get()


# Once the individual analysis is over, create the global report.
g_analysis = GlobalAnalysis(attrs, 'seeking', 'queueing','total', 'speed',
                   'mobility', 'elapsed')
g_analysis.load_matrices(sim_analysis)
g_analysis.load_single_attribute(sim_analysis, 'TOTAL_VEHICLES')
g_analysis.create_report()
