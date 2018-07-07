import pickle, networkx as nx
import random as rd
import init, mutate, bias, util

def init_population(pop_size, configs):
    init_type = str(configs['initial_net_type'])
    directed = util.boool(configs['directed'])

    ####################### INIT NET TYPES ########################################

    if directed: assert(init_type == 'load' or init_type == 'pickle load' or init_type == 'random')

    if (init_type == "load"):
        population = [nx.read_edgelist(configs['network_file'], nodetype=int, create_using=nx.DiGraph()) for i in range(pop_size)]

    elif (init_type == "pickle load"):
        pickled_net = pickle.load(configs['network_file'])
        population = [pickled_net.copy() for i in range(pop_size)]

    elif (init_type == 'random'):
        population = gen_rd_nets(pop_size, configs)

    else:
        print("ERROR in master.gen_init_population(): unknown init_type.")
        return

    if util.boool(configs['biased']):
        assert(not directed)
        if (configs['bias_on'] == 'nodes'): bias.assign_node_bias(population, configs['bias_distribution'])
        elif (configs['bias_on'] == 'edges'): bias.assign_edge_bias(population, configs['bias_distribution'])
        else: print("ERROR in net_generator(): unknown bias_on: " + str (configs['bias_on']))


    return population


#HELPER FUNCTIONS
def gen_rd_nets(pop_size, configs):
    start_size = int(configs['starting_size'])
    assert (start_size >= 8) #really should consider number of edges, but trying to avoid an infinite rewire scenario

    edge_node_ratio = float(configs['edge_to_node_ratio'])
    num_edges = int(start_size*edge_node_ratio)
    directed = util.boool(configs['directed'])
    num_input_nodes = int(configs['num_input_nodes'])
    num_output_nodes = int(configs['num_output_nodes'])
    varied_init_population = util.boool(configs['varied_init_population'])

    population = [nx.empty_graph(0) for i in range(pop_size)]  # those warnings are annoying

    if varied_init_population:  reps = pop_size
    else:                       reps = 1

    for rep in range(reps):

        if directed:
            population[rep] = nx.empty_graph(8, create_using=nx.DiGraph())

            for n in population[rep].nodes():
                population[rep].node[n]['layer'] = 'hidden'

            # init hidden layer
            num_add = int(edge_node_ratio * 8)
            mutate.add_edges(population[rep], num_add, configs)

            # input and output layers
            population[rep].graph['input_nodes'] = []
            population[rep].graph['output_nodes'] = []
            mutate.add_nodes(population[rep], num_input_nodes, configs, layer='input')
            mutate.add_nodes(population[rep], num_output_nodes, configs, layer='output')

            # more to hidden layer
            mutate.add_nodes(population[rep], start_size - 8, configs)

            # attempt to patch bias introduced into input and output wiring
            num_rewire = start_size * 10
            mutate.rewire(population[rep], num_rewire, configs)

            init_directed_attributes(population)


        else:
            population[rep] = nx.empty_graph(8, create_using=nx.DiGraph())

            num_add = int(edge_node_ratio * 8)
            mutate.add_edges(population[rep], num_add, configs)
            mutate.add_nodes(population[rep], start_size - 8, configs)

        # correct for off-by-one-errors since rounding occurs twice
        if (len(population[rep].edges()) == num_edges + 1): mutate.rm_edges(population[rep], 1, configs)
        if (len(population[rep].edges()) == num_edges - 1): mutate.add_edges(population[rep], 1, configs)

        mutate.ensure_single_cc(population[rep], configs)

    if not varied_init_population:
        population = [population[0].copy() for i in range(pop_size)]
        double_check(population[0], configs)

    else:
        double_check(population, configs)

    return population


def double_check(population, configs):
    start_size = int(configs['starting_size'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])
    num_edges = int(start_size*edge_node_ratio)
    directed = util.boool(configs['directed'])
    num_input_nodes = int(configs['num_input_nodes'])
    num_output_nodes = int(configs['num_output_nodes'])

    for p in population:
        if not directed:
            assert (len(p.edges()) == num_edges)
            assert (len(p.nodes()) == start_size)

        else:
            actual_size = start_size + num_input_nodes + num_output_nodes
            actual_num_edges = num_edges + int((num_input_nodes + num_output_nodes) * edge_node_ratio)
            assert (len(p.edges()) == actual_num_edges)
            assert (len(p.nodes()) == actual_size)


def init_directed_attributes(population):
    for p in population:

        p.graph['fitness'] = 0
        p.graph['error'] = 0
        for n in p.nodes():
            p.node[n]['state'] = None



def custom_to_directed(population):
    # changes all edges to directed edges
    # rand orientation of edges
    #note that highly connected graphs should merge directing and signing edges to one loop

    for p in range(len(population)):
        edge_list = population[p].edges()
        del population[p]

        population[p] = nx.DiGraph(edge_list)
        edge_list = population[p].edges()
        for edge in edge_list:
            if (rd.random() < .5):  #50% chance of reverse edge
                population[p].remove_edge(edge[0], edge[1])
                population[p].add_edge(edge[1], edge[0])


def assign_edge_weight(configs):
    #called by mutate

    distrib = configs['init_weight_distrib']

    if distrib == 'uniformPositive': return rd.uniform(0,1)

    elif distrib == 'uniform': return rd.uniform(-1,1)

    else: assert(False)
