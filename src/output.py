#!/usr/local/bin/python3
import csv, pickle, numpy as np, networkx as nx
import util, pressurize, bias
np.set_printoptions(formatter={'int_kind': lambda x:' {0:d}'.format(x)})


def master_info(population, gen, size, pop_size, num_survive, advice, BD_table, configs):
    output_dir = configs['output_directory']
    num_data_output = int(configs['num_data_output'])
    num_net_output = int(configs['num_net_output'])
    stop_condition = configs['stop_condition']

    if (stop_condition == 'size'):
        end = int(configs['ending_size'])
        #this sort of assumes simulation starts near size 0
    elif (stop_condition == 'generation'): end = int(configs['max_generations'])
    else: assert(False)

    if (num_data_output > 0):
        if (gen % int(end / num_data_output) == 0):
            popn_data(population, output_dir, gen)
            util.cluster_print(output_dir, "Master at gen " + str(gen) + ", with net size = " + str(size) + " nodes and " + str(len(population[0].net.edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))

    if (num_net_output > 0):
        if (gen % int(end / num_net_output) == 0):
            nx.write_edgelist(population[0].net, output_dir + "nets_nx/" + str(gen))
            pickle_file = output_dir + "/nets_pickled/" + str(gen)
            with open(pickle_file, 'wb') as file:
                pickle.dump(population[0].net, file)
            deg_distrib_csv(output_dir, population, gen)



def final_master_info(population, gen, configs):
    output_dir = configs['output_directory']

    nx.write_edgelist(population[0].net, output_dir+"/nets/"+str(gen))
    pickle_file = output_dir + "/pickle_nets/" + str(gen) + "_pickle"
    with open(pickle_file, 'wb') as file: pickle.dump(population[0].net, file)
    popn_data(population, output_dir, gen)
    #draw_nets.basic(population, output_dir, total_gens)

    if util.boool(configs['biased']):
        util.cluster_print(output_dir,"Pickling biases.")
        bias.pickle_bias(population[0].net, output_dir+"/bias", configs['bias_on'])



def init_csv(out_dir, configs):
 
    net_data_title = "Generation, Net Size, Fitness, Average Degree, Edge:Node Ratio, Mean Fitness, Variance in Fitness, Fitness_Div_#Edges, Fitness_Div_#Nodes\n"
    deg_distrib_title = "Generation, Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies, Degs, Deg Freqs\n"

    with open(out_dir+"/net_data.csv",'w') as csv_out:
        csv_out.write(net_data_title)
    with open(out_dir+"/degree_distrib.csv",'w') as csv_out:
        csv_out.write(deg_distrib_title) #just blanking the file

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        for config in configs:
            outConfigs.write(config + "," + str(configs[config]) + "\n")

    out_time = out_dir + "/timing.csv"
    with open(out_time, 'w') as out_timing:
        out_timing.write("Net Size, Presssurize Time\n")


def popn_data(population, output_dir, gen):

    if (population[0].net.edges()):
        output_csv = output_dir + "/net_data.csv"

        with open(output_csv, 'a') as output_file:
            output = csv.writer(output_file)

            all_fitness = np.array([population[p].fitness for p in range(len(population))])
            mean_fitness = np.mean(all_fitness)
            var_fitness = np.var(all_fitness)

            Net = population[0] #most fit net
            net = Net.net
            nets_info = [gen, len(net.nodes()), Net.fitness, sum(net.degree().values())/len(net.nodes()),len(net.edges())/len(net.nodes()), mean_fitness, var_fitness, Net.fitness/float(len(net.edges())), Net.fitness/float(len(net.nodes()))]

            output.writerow(nets_info)

def deg_distrib_csv(output_dir, population, gen):
    with open(output_dir + "/degree_distrib.csv", 'a') as deg_file:
        #only distribution of most fit net
        output = csv.writer(deg_file)

        distrib_info = []
        distrib_info.append(gen)
        distrib_info.append(len(population[0].net.nodes()))

        in_degrees, out_degrees = list(population[0].net.in_degree().values()), list(population[0].net.out_degree().values())

        indegs, indegs_freqs = np.unique(in_degrees, return_counts=True)
        indegs = np.array2string(indegs).replace('\n', '')
        indegs_freqs = np.array2string(indegs_freqs).replace('\n', '')
        distrib_info.append(indegs)
        distrib_info.append(indegs_freqs)

        outdegs, outdegs_freqs = np.unique(out_degrees, return_counts=True)
        outdegs = np.array2string(outdegs).replace('\n', '')
        outdegs_freqs = np.array2string(outdegs_freqs).replace('\n', '')
        distrib_info.append(outdegs)
        distrib_info.append(outdegs_freqs)

        degrees = list(population[0].net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        degs = np.array2string(degs).replace('\n', '')
        freqs = np.array2string(freqs).replace('\n', '')
        distrib_info.append(degs)
        distrib_info.append(freqs)

        output.writerow(distrib_info)

