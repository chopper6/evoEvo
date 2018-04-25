import mutate, util, pickle, numpy as np
from random import SystemRandom as sysRand


def gen_biases(configs):
    bias_on = configs['bias_on']
    distrib = configs['bias_distribution']

    num_mutns = mutate.num_mutations(float(configs['grow_mutation_frequency']))

    if bias_on == 'edges': num_biases = int(num_mutns * float(configs['edge_to_node_ratio']))
    elif bias_on=='nodes': num_biases = int(num_mutns)
    else: assert(False)

    biases = []
    for i in range(num_biases): biases.append(bias_score(distrib))

    return biases


def assign_node_bias(population, distrib):
    # assumes all nets in popn are the same size

    biases = []
    for n in range(len(population[0].net.nodes())):
        biases.append(bias_score(distrib))

    for p in range(len(population)):
        net = population[p].net
        b=0
        for n in net.nodes():
            assign_a_node_bias(net, n, distrib, given_bias=biases[b])
            b+=1

    return population

def assign_a_node_bias(net, node, distrib, given_bias=None):
    #redundant with assign_an_edge_bias()
    if given_bias: bias = given_bias
    else: bias = bias_score(distrib)
    net.node[node]['bias'] = bias


def assign_edge_bias(population, distrib):
    biases = []
    for e in range(len(population[0].net.edges())):
        biases.append(bias_score(distrib))

    for p in range(len(population)):
        net = population[p].net
        b = 0
        for e in net.edges():
            assign_an_edge_bias(net, e, distrib, given_bias=biases[b])
            b += 1

    return population


def assign_an_edge_bias(net, edge, distrib, given_bias=None):
    if given_bias:
        bias = given_bias

    else:
        bias = bias_score(distrib)

    net[edge[0]][edge[1]]['bias'] = bias


def bias_score(distrib):
    if (distrib == 'uniform'):
        return sysRand().uniform(0, 1)

    elif (distrib == 'normal'):
        bias = sysRand().normalvariate(.5, .2)
        if bias > 1:
            bias = 1
        elif bias < 0:
            bias = 0
        return bias

    elif (distrib == 'bi'):
        return sysRand().choice([.1, .9])

    elif (distrib == 'half'):
        return sysRand().choice([.5, 1])

    elif (distrib == 'global_small'):
        return .75
    elif (distrib == 'global_extreme'):
        return 1
    elif (distrib == 'global_extreme01'):
        return sysRand().choice([0, 1])

    else:
        print("ERROR in net_generator(): unknown bias distribution: " + str(distrib))
        assert(False)
        return 1



def pickle_bias(net, output_dir, bias_on): #for some reason bias_on isn't recognz'd

        degrees = list(net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))

        percent = True
        if (percent): freq = [(f/tot)*100 for f in freqs]

        #derive vals from conservation scores
        bias_vals, ngh_bias_vals = [], []
        for deg in degs: #deg bias is normalized by num nodes; node bias is normz by num edges
            avg_bias, ngh_bias, num_nodes = 0,0,0
            for node in net.nodes():
                if (len(net.in_edges(node))+len(net.out_edges(node)) == deg):
                    if (bias_on == 'nodes'):
                        avg_bias += abs(.5-net.node[node]['bias'])

                        avg_ngh_bias = 0
                        for ngh in net.neighbors(node):
                            avg_ngh_bias += net.node[ngh]['bias']

                        num_ngh = len(net.neighbors(node))
                        if num_ngh > 0: avg_ngh_bias /= num_ngh
                        ngh_bias += abs(.5-avg_ngh_bias)

                    elif (bias_on == 'edges'): #node bias is normalized by num edges
                        node_bias, num_edges = 0, 0
                        for edge in net.in_edges(node)+net.out_edges(node):
                            #poss err if out_edges are backwards

                            node_bias += (.5-net[edge[0]][edge[1]]['bias'])
                            num_edges += 1
                        node_bias = abs(node_bias)
                        if (num_edges != 0): node_bias /= num_edges
                        assert(num_edges == deg)
                        avg_bias += node_bias

                    num_nodes += 1

            avg_bias /= num_nodes
            ngh_bias /= num_nodes
            bias_vals.append(avg_bias)
            ngh_bias_vals.append(ngh_bias)
        assert(len(bias_vals) == len(degs))


        with open(output_dir + "/degs_freqs_bias",'wb') as file:
            pickle.dump( [degs, freqs, bias_vals] , file)

