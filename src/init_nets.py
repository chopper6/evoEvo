import pickle, networkx as nx
from random import SystemRandom as sysRand
import init, mutate, bias, util

# maybe rename to reduce confusion
class Net:
    def __init__(self, net, id):
        self.fitness = 0
        self.net = net.copy()
        #assert(self.net != net)
        self.id = id  #not curr used

    def copy(self):
        copy = Net(self.net, self.id)
        copy.fitness = self.fitness
        #assert (copy != self and copy.net != self.net)
        #assert (copy.fitness_parts != self.fitness_parts)
        return copy


def init_population(init_type, start_size, pop_size, configs):
    sign_edges_needed = True
    edge_node_ratio = float(configs['edge_to_node_ratio'])
    num_edges = int(start_size*edge_node_ratio)



    ####################### MAIN INIT NET TYPES USED ########################################
    if (init_type == "load"):
        population = [Net(nx.read_edgelist(configs['network_file'], nodetype=int, create_using=nx.DiGraph()), i) for i
                      in range(pop_size)]

    elif (init_type == "pickle load"):
        pickled_net = pickle.load(configs['network_file'])
        population = [Net(pickled_net.copy(), i) for i in range(pop_size)]
        sign_edges_needed = False

    elif (init_type == 'random'):

        if (start_size <= 20):
            init_net = nx.empty_graph(start_size, create_using=nx.DiGraph())
            num_add = int(edge_node_ratio * start_size)
            mutate.add_edges(init_net, num_add, configs)

        else:  # otherwise rewire till connected is intractable, grow without selection instead
            init_net = nx.empty_graph(8, create_using=nx.DiGraph())
            num_add = int(edge_node_ratio * 8)
            mutate.add_edges(init_net, num_add, configs)
            mutate.add_nodes(init_net, start_size - 8, configs)

            #correct for off-by-one-errors since rounding occurs twice
            if (len(init_net.edges()) == num_edges+1): mutate.rm_edges(init_net, 1, configs)
            if (len(init_net.edges()) == num_edges-1): mutate.add_edges(init_net, 1, configs)

        mutate.ensure_single_cc(init_net, configs)
        assert (len(init_net.edges()) == num_edges)
        assert (len(init_net.nodes()) == start_size)

        population = [Net(init_net.copy(), i) for i in range(pop_size)]




    ####################### OTHER NET TYPES, POSSIBLY OUTDATED ########################################
    elif (init_type == 'shell'):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)]  # change to generate, based on start_size

    elif (init_type == 'erdos-renyi'):
        num_cc = 2
        num_tries = 0
        while(num_cc != 1):
            num_tries += 1
            init_net = (nx.erdos_renyi_graph(start_size,.035, directed=True, seed=None))
            num_added = 0
            for node in init_net.nodes():
                if (init_net.degree(node) == 0):
                    pre_edges = len(init_net.edges())
                    num_added += 1
                    sign = sysRand().randint(0, 1)
                    if (sign == 0):     sign = -1
                    node2 = node
                    while (node2 == node):
                        node2 = sysRand().sample(init_net.nodes(), 1)
                        node2 = node2[0]
                    if (sysRand().random() < .5): init_net.add_edge(node, node2, sign=sign)
                    else: init_net.add_edge(node2, node, sign=sign)
                    assert (len(init_net.edges()) > pre_edges)
                else:
                    if (init_net.in_edges(node) + init_net.out_edges(node) == 0): print("ERROR in net_generator(): hit a 0 deg node that is unrecognized.")

            net_undir = init_net.to_undirected()
            num_cc = nx.number_connected_components(net_undir)

        print("Number of added edges to avoid 0 degree = " + str(num_added) + ", num attempts to create suitable net = " + str(num_cc) + ".\n")
        population = [Net(init_net.copy(), i) for i in range(pop_size)]

    elif (init_type == 'empty'):
        population = [Net(nx.empty_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'complete'):
        #crazy high run time due to about n^n edges
        population = [Net(nx.complete_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'cycle'):
        population = [Net(nx.cycle_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'star'):
        population = [Net(nx.star_graph(start_size-1), i) for i in range(pop_size)]
        custom_to_directed(population)

    elif (init_type == 'v sparse erdos-renyi'):
        num_cc = 2
        num_tries = 0
        while(num_cc != 1):
            num_tries += 1
            init_net = (nx.erdos_renyi_graph(start_size,.002, directed=True, seed=None))
            num_added = 0
            for node in init_net.nodes():
                if (init_net.degree(node) == 0):
                    pre_edges = len(init_net.edges())
                    num_added += 1
                    sign = sysRand().randint(0, 1)
                    if (sign == 0):     sign = -1
                    node2 = node
                    while (node2 == node):
                        node2 = sysRand().sample(init_net.nodes(), 1)
                        node2 = node2[0]
                    if (sysRand().random() < .5): init_net.add_edge(node, node2, sign=sign)
                    else: init_net.add_edge(node2, node, sign=sign)
                    assert (len(init_net.edges()) > pre_edges)
                else:
                    if (init_net.in_edges(node) + init_net.out_edges(node) == 0): print("ERROR in net_generator(): hit a 0 deg node that is unrecognized.")

            net_undir = init_net.to_undirected()
            num_cc = nx.number_connected_components(net_undir)

        print("Number of added edges to avoid 0 degree = " + str(num_added) + ", num attempts to create suitable net = " + str(num_cc) + ".\n")
        population = [Net(init_net.copy(), i) for i in range(pop_size)]


    elif (init_type == 'scale-free'):  # curr does not work, since can't go to undirected for output
        population = [Net(nx.scale_free_graph(start_size, beta=.7, gamma=.15, alpha=.15),i) for i in range(pop_size)]
    elif (init_type == 'barabasi-albert 2'):
        population = [Net(nx.barabasi_albert_graph(start_size, 2),i) for i in range(pop_size)]
        custom_to_directed(population)
    elif (init_type == 'barabasi-albert 1'):
        population = [Net(nx.barabasi_albert_graph(start_size, 1),i) for i in range(pop_size)]
        custom_to_directed(population)

    elif (init_type == 'double cycle'): #double cycle
        population = [Net(nx.cycle_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]
        double_edges(population)

    elif (init_type == 'double star'): #double star
        population = [Net(nx.star_graph(start_size-1), i) for i in range(pop_size)]
        custom_to_directed(population)
        double_edges(population)

    elif (init_type == 'exponential'): #may be a bit slow
        init_net = Net(nx.cycle_graph(start_size, create_using=nx.DiGraph()),0)
        double_edges([init_net])
        sign_edges([init_net])
        sign_edges_needed = False
        num_rewire = start_size*10
        mutate.rewire(init_net.net, num_rewire)

        population = [Net(init_net.net.copy(), i) for i in range(pop_size)]
        assert(population[0] != population[1] and population[0].net != population[1].net)

    elif (init_type == "vinayagam"):
        population = [Net(init.load_network(configs), i) for i in range(pop_size)]

    elif (init_type == 'All Leaves'):
        population = [Net(nx.configuration_model([1 for e in range(start_size)]),i) for i in range(pop_size)]

    elif (init_type == 'All 2s'):
        population = [Net(nx.configuration_model([2 for e in range(start_size)]),i) for i in range(pop_size)]

    elif (init_type == 'All 3s'):
        population = [Net(nx.configuration_model([3 for e in range(start_size)]),i) for i in range(pop_size)]


    else:
        print("ERROR in master.gen_init_population(): unknown init_type.")
        return

    if (sign_edges_needed == True): sign_edges(population)
    if util.boool(configs['biased']):
        if (configs['bias_on'] == 'nodes'): bias.assign_node_bias(population, configs['bias_distribution'])
        elif (configs['bias_on'] == 'edges'): bias.assign_edge_bias(population, configs['bias_distribution'])
        else: print("ERROR in net_generator(): unknown bias_on: " + str (configs['bias_on']))
    return population


#HELPER FUNCTIONS
def custom_to_directed(population):
    # changes all edges to directed edges
    # rand orientation of edges
    #note that highly connected graphs should merge directing and signing edges to one loop

    for p in range(len(population)):
        edge_list = population[p].net.edges()
        del population[p].net

        population[p].net = nx.DiGraph(edge_list)
        edge_list = population[p].net.edges()
        for edge in edge_list:
            if (sysRand().random() < .5):  #50% chance of reverse edge
                population[p].net.remove_edge(edge[0], edge[1])
                population[p].net.add_edge(edge[1], edge[0])


def sign_edges(population):
    for p in range(len(population)):
        edge_list = population[p].net.edges()
        for edge in edge_list:
            sign = sysRand().randint(0, 1)
            if (sign == 0):     sign = -1
            population[p].net[edge[0]][edge[1]]['sign'] = sign


def sign_edges_single(net):
    edge_list = net.edges()
    for edge in edge_list:
        sign = sysRand().randint(0, 1)
        if (sign == 0):     sign = -1
        net[edge[0]][edge[1]]['sign'] = sign


def double_edges(population):
    for p in range(len(population)):
        net = population[p].net
        edges = net.edges()
        for edge in edges:
            net.add_edge(edge[1], edge[0])  # add reverse edge

