#!/usr/bin/python3
import os,sys,csv,shutil
from mpi4py import MPI
import init, util, plot_nets
import numpy as np
from time import sleep

# WARNING: MULTIPLE SIMULATIONS MAY BE OUTDATED

def evolve(config_file):

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_workers = comm.Get_size()-1  # master not incld

    configs = init.load_sim_configs(config_file, rank)
    orig_output_dir = configs['output_directory']
    num_sims = int(configs['num_sims'])
    debug = util.boool(configs['debug'])

    num_workers_config = int(configs['number_of_workers'])
    assert(num_workers == num_workers_config or debug)
    assert(num_workers > 0 or debug)

    for i in range(num_sims):

        init_sim(configs, num_sims, i, orig_output_dir,rank)

        if rank == 0:  # MASTER
            if (num_sims > 1):
                util.cluster_print(orig_output_dir, "\n##################################### STARTING EVOLUTION OF SIM #" + str(i) + " #####################################\n")

            log_text = 'Evolve_root(): in dir ' + str(os.getcwd()) + ', config file = ' + str(config_file) + ', num_workers = ' + str(num_workers) + "\n"

            import master
            util.cluster_print(configs['output_directory'], log_text)
            master.evolve_master(configs)

        else: # WORKERS
            import minion
            minion.work(configs, rank)

    if (num_sims > 1 and rank==0):
        util.cluster_print(configs['output_directory'], "COMBINING AND PLOTTING MULTIPLE SIM...")
        close_out_mult_sims(num_sims, orig_output_dir, configs)


    if (rank==0):
        util.cluster_print(configs['output_directory'], "\nDone. Exiting Evolution.\n")
        comm.Abort()



def init_sim(configs, num_sims, sim_num, orig_output_dir, rank):
    if (num_sims > 1 and sim_num == 0):  # check where to pick up the run
        this_dir = False
        curr_dir=0
        while (not this_dir):

            if (sim_num >= num_sims):
                util.cluster_print(orig_output_dir, "All simulations already finished, exiting...\n")
                return 1

            configs['output_directory'] = orig_output_dir + "_" + str(curr_dir)
            this_dir = True  # remains true if any of the following fail

            if os.path.exists(configs['output_directory'] + "/progress.txt"):
                with open(configs['output_directory'] + "/progress.txt") as progress:
                    line = progress.readline()
                    if (line.strip() == 'Done' or line.strip() == 'done'):
                        this_dir = False
                        sim_num += 1

            curr_dir+=1

    if (num_sims > 1):
        configs['output_directory'] = orig_output_dir + "sim_" + str(sim_num) + "/"
        if (rank == 0):
            if not os.path.exists(configs['output_directory']): os.makedirs(configs['output_directory'])
        else:
            while (not os.path.exists(configs['output_directory'])):
                sleep(1)


def close_out_mult_sims(num_sims, orig_output_dir, configs):
    extract_and_combine(orig_output_dir, num_sims)
    plot_nets.all_plots(configs, indiv_plots=False, orig_output_directory=orig_output_dir, var=True)

    rm_base_dirs = True
    if rm_base_dirs:
        for i in range(num_sims-1): #keep one of em
            if (os.path.exists(orig_output_dir + "sim_" + str(i))):
                shutil.rmtree(orig_output_dir + "sim_" + str(i)) #clean up, leave last run as sample

        if (os.path.isfile(orig_output_dir + "sim_" + str(num_sims) + "/net_data.csv" )):
            os.remove(orig_output_dir + "sim_" + str(num_sims) + "/net_data.csv") #otherwise will confuse multiple plots


def extract_and_combine(output_dir, num_sims):
    # takes info.csv from mult runs and combines into one info.csv in main dir

    all_data, titles = None, None #just for warnings

    for i in range(num_sims):
        info_file = output_dir + "sim_" + str(i) + "/net_data.csv"

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
    var_data = np.empty((len(lines)-1, len(titles)))
    for i in range(len(lines)-1):
        for j in range(len(titles)):
            a_mean_data = np.mean(all_data[:,i,j])
            mean_data[i][j] = a_mean_data
            a_var_data = np.var(all_data[:,i,j])
            var_data[i][j] = a_var_data

    with open(output_dir + "/net_data.csv", 'w') as final_info:
        file = csv.writer(final_info)
        titles[-1] = titles[-1].replace("\n",'')
        file.writerow(titles)
        for row in mean_data:
            file.writerow(row)

    with open(output_dir + "/net_data_variance.csv", 'w') as final_info:
        file = csv.writer(final_info)
        titles[-1] = titles[-1].replace("\n",'')
        file.writerow(titles)
        for row in var_data:
            file.writerow(row)

if __name__ == "__main__":
    # note that yamaska and rupert should call this directly
    # guillimin calls through batch_root
    config_file = sys.argv[1]
    evolve(config_file)

