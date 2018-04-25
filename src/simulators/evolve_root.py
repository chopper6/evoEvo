#!/usr/bin/python3
import os,sys,csv,shutil
from mpi4py import MPI
#os.environ['lib'] = '/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib' #NOTE: needed only for yamaska/rupert
sys.path.insert(0, os.getenv('lib'))
import init, util, plot_nets
import numpy as np
from time import sleep

# WARNING: MULTIPLE SIMULATIONS MAY BE OUTDATED

def evolve(rank, num_workers, config_file):

    configs = init.load_sim_configs(config_file, rank, num_workers)
    orig_output_dir = configs['output_directory']
    num_sims = int(configs['num_sims'])

    for i in range(num_sims):

        init_sim(configs, num_sims, i, orig_output_dir)

        if rank == 0:  # MASTER
            log_text = 'Evolve_root(): in dir ' + str(os.getcwd()) + ', config file = ' + str(config_file) + ', num_workers = ' + str(num_workers) + "\n"

            import master
            util.cluster_print(configs['output_directory'], log_text)
            master.evolve_master(configs)

        else: # WORKERS
            import minion
            minion.work(configs, rank)

    if (num_sims > 1 and rank==0): close_out_mult_sims(num_sims, orig_output_dir)


def init_sim(configs, num_sims, sim_num, orig_output_dir):
    if (num_sims > 1 and sim_num == 0):  # check where to pick up the run
        this_dir = False
        while (not this_dir):

            if (sim_num >= num_sims):
                util.cluster_print(orig_output_dir, "All simulations already finished, exiting...\n")
                return

            configs['output_directory'] = orig_output_dir + "_" + str(i)
            this_dir = True  # remains true if any of the following fail

            if os.path.exists(configs['output_directory'] + "/progress.txt"):
                with open(configs['output_directory'] + "/progress.txt") as progress:
                    line = progress.readline()
                    if (line.strip() == 'Done' or line.strip() == 'done'):
                        this_dir = False
                        sim_num += 1

    if (num_sims > 1):
        configs['output_directory'] = orig_output_dir + "sim_" + str(sim_num) + "/"
        configs['instance_file'] = (util.slash(configs['output_directory']) + "/instances/" + configs['stamp'])
        if (rank == 0):
            if not os.path.exists(configs['output_directory']): os.makedirs(configs['output_directory'])
        else:
            while (not os.path.exists(configs['output_directory'])):
                sleep(1)


def close_out_mult_sims(num_sims, orig_output_dir):
    extract_and_combine(orig_output_dir, num_sims)
    plot_nets.feature_plots_only(orig_output_dir)
    for i in range(num_sims-1):
        if (os.path.exists(orig_output_dir + "sim_" + str(i))):
            shutil.rmtree(orig_output_dir + "sim_" + str(i)) #clean up, leave last run as sample


def extract_and_combine(output_dir, num_sims):
    # takes info.csv from mult runs and combines into one info.csv in main dir
    all_data, titles = None, None #just for warnings

    for i in range(num_sims):
        info_file = output_dir + "sim_" + str(i) + "/info.csv"

        if (os.path.isfile(info_file)):
            with open(info_file) as info:
                lines = info.readlines()

                if (i==0):
                    titles = lines[0].split(',')
                    all_data = np.empty((num_sims, len(lines)-1, len(titles)))

                j=0
                for line in lines[1:]:
                    data = line.split(',')
                    all_data[i][j] = data
                    j+=1

        else: print("ERROR evolve_root.extract(): no file found: " + str(info_file))

    mean_data = np.empty((len(lines)-1, len(titles)))
    for i in range(len(lines)-1):
        for j in range(len(titles)):
            a_mean_data = np.mean(all_data[:,i,j])
            mean_data[i][j] = a_mean_data

    with open(output_dir + "/info.csv", 'w') as final_info:
        file = csv.writer(final_info)
        titles[-1] = titles[-1].replace("\n",'')
        file.writerow(titles)
        for row in mean_data:
            file.writerow(row)

if __name__ == "__main__":
    # note that yamaska and rupert should call this directly
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_workers = comm.Get_size()-1  # master not incld
    config_file = sys.argv[1]

    evolve(rank, num_workers, config_file)

    if (rank==0):
        comm.Abort()
        print("\nExiting Evolution.\n")
