# this file is in the initial git repo, but not further tracked
# paths should be specific to whatever cluster set up is relevant

def get():

    input_base_dir = "/home/chopper/evoEvo/data/input/"

    simulation_script = "/home/chopper/evoEvo/src/roots/evolve.py"
    simulation_batch_root = "/home/chopper/evoEvo/src/roots/batch.py"
    launching_script = "/home/chopper/evoEvo/src/launchers/launcher.py"
    simulation_directory = "/home/chopper/evoEvo/src/simulators/"
    launching_directory =  "/home/chopper/evoEvo/src/launchers/"

    return simulation_script, simulation_batch_root, launching_script, simulation_directory, launching_directory, input_base_dir