import sys, os, time, math
import util

#--------------------------------------------------------------------------------------------------
def load_sim_configs (param_file, rank):
    parameters = (open(param_file,'r')).readlines()
    assert len(parameters)>0
    configs = {}
    for param in parameters:
        if len(param) > 0: #ignore empty lines
            if param[0] != '#': #ignore lines beginning with #
                param = param.split('=')
                if len (param) == 2:
                    key   = param[0].strip().replace (' ', '_')
                    value = param[1].strip()
                    configs[key] = value

    configs['timestamp']           = time.strftime("%B-%d-%Y-h%Hm%Ms%S")
    configs ['output_directory'] += "/"

    #--------------------------------------------

    if rank == 0: #only master should create dir, prevents workers from fighting over creating the same dir
        tries = 0
        while not os.path.isdir (configs['output_directory']):
            try:
                os.makedirs (configs['output_directory']) # will raise an error if invalid path, which is good
            except:
                tries += 1
                if tries == 1000: print('WARNING: init.py master may be stuck in a loop failing to create output directory')
                time.sleep(5)
                continue

        #this is now checked further up in evolve_root
        #if (int(configs['number_of_workers']) != num_workers): util.cluster_print(configs['output_directory'],"\nWARNING in init.load_sim_configs(): mpi #workers != config #workers! " + str(configs['number_of_workers']) + " vs " + str(num_workers) + "\n")  # not sure why this doesn't correctly get # config workers...

    if (configs['stop_condition'] == 'size'):
        assert(int(configs['grow_mutation_frequency']) > 0)
    return configs


#--------------------------------------------------------------------------------------------------
def build_advice(net, configs):
    if (configs['advice_creation'] == 'once'):
        #assumes no growth
        advice_upon = configs['advice_upon']
        biased = util.boool(configs['biased'])
        bias_on = str(configs['bias_on'])
        pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
        samples, sample_size = None, None

        if (advice_upon == 'nodes'):
            samples = net.nodes()
            sample_size = int(pressure * len(net.nodes()))
        elif (advice_upon == 'edges'):
            samples = [[str(node_i), str(node_j)] for node_i in net.nodes() for node_j in net.nodes()]  # all possible edges
            #samples = net.edges()
            sample_size = int(pressure * len(net.edges())) #sample size based on all existing edges
        advice = util.advice (net, util.sample_p_elements(samples,sample_size), biased, advice_upon, bias_on)
    else: advice = None #will generate during reduction each time instead

    return advice
