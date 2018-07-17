import pickle, networkx as nx, random as rd, math
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
    num_init_nodes = min_num_nodes(configs)
    assert (start_size >= num_init_nodes)

    edge_node_ratio = float(configs['edge_to_node_ratio'])
    directed = util.boool(configs['directed'])
    num_input_nodes = int(configs['num_input_nodes'])
    num_output_nodes = int(configs['num_output_nodes'])
    varied_init_population = util.boool(configs['varied_init_population'])
    single_cc = util.boool(configs['single_cc'])



    if varied_init_population:
        population = [nx.empty_graph(num_init_nodes, create_using=nx.DiGraph()) for i in range(pop_size)]
        if directed: init_directed_attributes(population, configs)
        reps = pop_size
    else:
        population = [None for i in range(pop_size)]
        population[0] = nx.empty_graph(num_init_nodes, create_using=nx.DiGraph())
        if directed: init_directed_attributes([population[0]], configs)
        reps = 1

    for rep in range(reps):

        if directed:
            net = population[rep]

            # init hidden layer
            num_add = round(edge_node_ratio * num_init_nodes)
            mutate.add_edges(net, num_add, configs)

            if single_cc: mutate.ensure_single_cc(net, configs)
            # because init_nets for example can add to a previously node-only graph, which should then be connected

            # input and output layers
            assert(num_input_nodes > 0 and num_output_nodes > 0)
            net.graph['input_nodes'], net.graph['output_nodes'] = [], []
            mutate.add_nodes(net, num_output_nodes, configs, layer='output', init=True)
            mutate.add_nodes(net, num_input_nodes, configs, layer='input', init=True)

            # more to hidden layer
            mutate.add_nodes(net, start_size - num_init_nodes, configs, init=True)


            # attempt to patch bias introduced into input and output wiring
            num_rewire = len(net.edges()) * 10
            mutate.rewire(net, num_rewire, configs)


        else:
            net = nx.empty_graph(8, create_using=nx.DiGraph())

            num_add = round(edge_node_ratio * 8)
            mutate.add_edges(net, num_add, configs)
            if single_cc: mutate.ensure_single_cc(net, configs)
            mutate.add_nodes(net, start_size - 8, configs, init=True)


        mutate.ensure_single_cc(net, configs)
        if directed: mutate.check_layers(net, configs)

    if not varied_init_population:
        population = [population[0].copy() for i in range(pop_size)]
        double_check([population[0]], configs)

    else:
        double_check(population, configs)

    return population



def min_num_nodes(configs):

    directed = util.boool(configs['directed'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])
    self_loops = util.boool(configs['self_loops'])

    assert(directed) #too lazy to make undirected version now

    if self_loops:
        min_num = edge_node_ratio
    else:
        min_num = edge_node_ratio + 1

    min_num_for_inputs = math.ceil(float(configs['from_inputs_edge_ratio']))
    min_num_for_outputs = math.ceil(float(configs['to_outputs_edge_ratio']))

    return max(min_num, min_num_for_inputs, min_num_for_outputs)


def double_check(population, configs):
    #TODO: eventually cut this for time sake

    start_size = int(configs['starting_size'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])
    num_edges = round(start_size*edge_node_ratio)
    directed = util.boool(configs['directed'])
    num_input_nodes = int(configs['num_input_nodes'])
    num_output_nodes = int(configs['num_output_nodes'])

    for p in population:
        if not directed:
            assert (len(p.edges()) == num_edges)
            assert (len(p.nodes()) == start_size)

        else:
            actual_size = start_size + num_input_nodes + num_output_nodes
            #actual_num_edges = num_edges + int((num_input_nodes + num_output_nodes) * edge_node_ratio)
            #assert (len(p.edges()) == actual_num_edges)
            #assert (len(p.nodes()) == actual_size)


        #if not util.boool(configs['in_edges_to_inputs']):
        for i in p.graph['input_nodes']:
            assert(not p.in_edges(i))


        if not util.boool(configs['out_edges_from_outputs']):
            for o in p.graph['output_nodes']:
                assert(not p.out_edges(o))


def init_directed_attributes(population, configs):
    for p in population:

        p.graph['fitness'] = 0
        p.graph['error'] = 0

        p.graph['input'] = None
        p.graph['output'] = None
        p.graph['prev_input'] = None
        p.graph['prev_output'] = None

        # THESE SHOULD JUST BE FOR THE INITIAL NODES OF THE EMPTY GRAPH
        for n in p.nodes():
            p.node[n]['state'] = None
            p.node[n]['neuron_bias'] = assign_edge_weight(configs)
            p.node[n]['layer'] = 'hidden'


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
    elif distrib == 'small_uniform': return rd.uniform(-.1,.1)

    else: assert(False)


def assign_bias_weight(configs):
    #called by mutate
    basis = 'activation'

    if basis == 'activation':
        activn_fn = configs['activation_function']
        if activn_fn == 'sigmoid':
            return rd.uniform(0,1)
        elif activn_fn == 'tanh':
            return rd.uniform(-1,1)

    elif basis == 'distribution':
        distrib = configs['init_weight_distrib']
        if distrib == 'uniformPositive':
            return rd.uniform(0, 1)
        elif distrib == 'uniform':
            return rd.uniform(-1, 1)

    else: assert(False)


def print_inout_edges(net, configs):
    # just used for debugging

    num_input_nodes = int(configs['num_input_nodes'])
    num_output_nodes = int(configs['num_output_nodes'])
    num_reservoir_edges = len(net.edges()) - len(net.in_edges(net.graph['output_nodes'])) - len(net.out_edges(net.graph['input_nodes']))
    start_size = int(configs['starting_size'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])
    num_edges = round(start_size*edge_node_ratio)

    print("# output edges = " + str(len(net.in_edges(net.graph['output_nodes']))) + " vs " + str(
        round(num_output_nodes * float(configs['to_outputs_edge_ratio']))))
    print("# input edges = " + str(len(net.out_edges(net.graph['input_nodes']))) + " vs " + str(
        round(num_input_nodes * float(configs['from_inputs_edge_ratio']))))
    print("# reservoir edges = " + str(num_reservoir_edges) + " vs " + str(num_edges))
