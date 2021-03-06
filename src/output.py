#!/usr/local/bin/python3
import csv, pickle, numpy as np, networkx as nx
import util, pressurize, bias
np.set_printoptions(formatter={'int_kind': lambda x:' {0:d}'.format(x)})


def master_info(population, gen, size, pop_size, num_survive, configs):
    output_dir = configs['output_directory']
    num_data_output = int(configs['num_data_output'])
    num_net_output = int(configs['num_net_output'])
    stop_condition = configs['stop_condition']

    if (stop_condition == 'size'):
        end = int(configs['ending_size'])
        start = int(configs['starting_size'])
        assert(end-start >= num_data_output and end-start >= num_net_output)
        #this sort of assumes simulation starts near size 0
    elif (stop_condition == 'generation' or stop_condition == 'gen'):
        end = int(configs['max_generations'])
        start = 0
        assert(end >= num_data_output and end >= num_net_output)
    else: assert(False)

    if (num_data_output > 0):
        if (gen % int((end-start) / num_data_output) == 0):
            popn_data(population, output_dir, gen, configs)
            util.cluster_print(output_dir, "Master at gen " + str(gen) + ", with net size = " + str(len(population[0].nodes())) + " nodes and " + str(len(population[0].edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))

    if (num_net_output > 0):
        if (gen % int((end-start) / num_net_output) == 0):
            nx.write_edgelist(population[0], output_dir + "nets_nx/" + str(gen))
            pickle_file = output_dir + "/nets_pickled/" + str(gen)
            with open(pickle_file, 'wb') as file:
                pickle.dump(population[0], file)
            deg_distrib_csv(output_dir, population, gen, configs)



def final_master_info(population, gen, configs):
    output_dir = configs['output_directory']

    nx.write_edgelist(population[0], output_dir+"/nets_nx/"+str(gen))
    pickle_file = output_dir + "/nets_pickled/" + str(gen)
    with open(pickle_file, 'wb') as file: pickle.dump(population[0], file)
    popn_data(population, output_dir, gen, configs)
    deg_distrib_csv(output_dir, population, gen, configs)
    #draw_nets.basic(population, output_dir, total_gens)

    if util.boool(configs['biased']):
        util.cluster_print(output_dir,"Pickling biases.")
        bias.pickle_bias(population[0], output_dir+"/bias", configs['bias_on'])


def write_base_features(configs, gen, iter, err, curr_fitness):
    output_dir = configs['output_directory']
    num_net_output = int(configs['num_net_output'])
    stop_condition = configs['stop_condition']

    if (stop_condition == 'size'):
        end = int(configs['ending_size'])
        start = int(configs['starting_size'])
        #this sort of assumes simulation starts near size 0
    elif (stop_condition == 'generation' or stop_condition == 'gen'):
        end = int(configs['max_generations'])
        start = 0
    else: assert(False)

    if (num_net_output > 0):
        if (gen % int((end-start) / num_net_output) == 0):

            with open(output_dir+"/base_problem/error.csv",'a') as csv_out:
                csv_out.write(str(gen) + "," + str(iter) + "," + str(err) + "\n")


            with open(output_dir+"/base_problem/fitness.csv",'a') as csv_out:
                csv_out.write(str(gen) + "," + str(iter) + "," + str(curr_fitness) + "\n")



def init_csv(out_dir, configs):
 

    if util.boool(configs['directed']):
        net_data_title = "Generation, Net Size, Fitness, Average Degree, Edge:Node Ratio, Fitness Mean, Fitness Variance, Fitness_Div_#Edges, Fitness_Div_#Nodes, Error of Base Problem," \
                         "Diameter, Assortativity by Degree, Assortativity by State, Clustering Coefficient,"\
                         "Assortativity by Degree x #Nodes, Assortativity by State x #Nodes, Clustering Coefficient x #Nodes,"\
                         "#In Edges to Outputs, #Out Edges from Inputs, #Out Edges from Errors\n"


    else:
        #net_data_title = "Generation, Net Size, Fitness, Average Degree, Edge:Node Ratio, Mean Fitness, Variance in Fitness, Fitness_Div_#Edges, Fitness_Div_#Nodes, Error of Base Problem, Diameter\n"
        net_data_title = "Generation, Net Size, Fitness, Average Degree, Edge:Node Ratio, Mean Fitness, Variance in Fitness, Fitness_Div_#Edges, Fitness_Div_#Nodes, Diameter\n"

    deg_distrib_title = "Generation, Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies, Degs, Deg Freqs\n"
    err_file_title = "Generation, Iteration, Error (MSE)\n"
    fitness_title = "Generation, Iteration, " + str(configs['fitness_metric']) + "\n"


    with open(out_dir+"/net_data.csv",'w') as csv_out:
        csv_out.write(net_data_title)
    with open(out_dir+"/degree_distrib.csv",'w') as csv_out:
        csv_out.write(deg_distrib_title)
    with open(out_dir+"/base_problem/error.csv",'w') as csv_out:
        csv_out.write(err_file_title)
    with open(out_dir + "/base_problem/fitness.csv", 'w') as csv_out:
        csv_out.write(fitness_title)

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        for config in configs:
            outConfigs.write(config + "," + str(configs[config]) + "\n")


def popn_data(population, output_dir, gen, configs):

    #assert(util.boool(configs['directed'])) #pretty simple fix for undirected features, but I'm lazy
    scale_node_fitness = configs['scale_node_fitness']

    if (population[0].edges()):
        output_csv = output_dir + "/net_data.csv"

        with open(output_csv, 'a') as output_file:
            output = csv.writer(output_file)

            if scale_node_fitness: all_fitness = np.array([population[p].graph['fitness'] for p in range(len(population))])
            else: all_fitness = np.array([population[p].graph['fitness']/len(population[p].nodes()) for p in range(len(population))])
            mean_fitness = np.mean(all_fitness)
            var_fitness = np.var(all_fitness)

            net = population[0] #most fit net
            undir = net.to_undirected()
            nets_info = [gen, len(net.nodes()), net.graph['fitness'], sum(net.degree().values())/len(net.nodes()),len(net.edges())/len(net.nodes()),
                         mean_fitness, var_fitness, net.graph['fitness']/float(len(net.edges())), net.graph['fitness']/float(len(net.nodes())), nx.diameter(undir)]

            if util.boool(configs['directed']):
                nets_info.append(len(net.in_edges(net.graph['output_nodes'])))
                nets_info.append(len(net.out_edges(net.graph['input_nodes'])))
                nets_info.append(len(net.out_edges(net.graph['error_nodes'])))



            output.writerow(nets_info)

def deg_distrib_csv(output_dir, population, gen, configs):
    with open(output_dir + "/degree_distrib.csv", 'a') as deg_file:
        #only distribution of most fit net
        output = csv.writer(deg_file)

        distrib_info = []
        distrib_info.append(gen)
        distrib_info.append(len(population[0].nodes()))

        reservoir_nodes = []
        if util.boool(configs['directed']):
            for n in population[0].nodes():
                if population[0].node[n]['layer'] == 'hidden': reservoir_nodes.append(n) #this will throw an error if undirected version
        else:
            for n in population[0].nodes(): reservoir_nodes.append(n)

        in_degrees, out_degrees = list(population[0].in_degree(reservoir_nodes).values()), list(population[0].out_degree(reservoir_nodes).values())

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

        degrees = list(population[0].degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        degs = np.array2string(degs).replace('\n', '')
        freqs = np.array2string(freqs).replace('\n', '')
        distrib_info.append(degs)
        distrib_info.append(freqs)

        output.writerow(distrib_info)

