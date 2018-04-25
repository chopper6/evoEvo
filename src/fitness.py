import math
from operator import attrgetter
import node_fitness

def eval_fitness(population, fitness_direction):
    #determines fitness of each individual and orders the population by fitness
    if (fitness_direction == 'max'): population = sorted(population,key=attrgetter('fitness'), reverse=True)
    elif (fitness_direction == 'min'):  population = sorted(population,key=attrgetter('fitness'))
    else: print("ERROR in fitness.eval_fitness(): unknown fitness_direction " + str(fitness_direction) + ", population not sorted.")

    return population

def calc_node_fitness(net, fitness_metric, directed):
    if directed:
        for n in net.nodes():
            up_in, up_out, down_in, down_out = net.node[n]['up_in'], net.node[n]['up_out'], net.node[n]['down_in'], net.node[n]['down_out']
            net.node[n]['fitness'] += node_fitness.calc_directed(fitness_metric, up_in, up_out, down_in, down_out)

    else:
        for n in net.nodes():
            up, down = net.node[n]['up'], net.node[n]['down']
            net.node[n]['fitness'] += node_fitness.calc_undirected(fitness_metric, up,down)


def node_product(net, scale_node_fitness):
    fitness_score = 0
    num_0 = 0
    num_under, num_over = 0,0
    for n in net.nodes():
        if net.node[n]['fitness'] == 0:
            num_0 += 1
        else:
            if scale_node_fitness: #hasn't really worked so far, in progress
                e2n = len(net.edges(n))
                Inode = net.node[n]['fitness']
                fitness_score += -1*math.log(net.node[n]['fitness'])
            else:
                fitness_score += -1*math.log(net.node[n]['fitness'],2)

    if (num_over != 0 or num_under != 0):
        print("# I < 0 = " + str(num_under) + "\t # I > 1 = " + str(num_over) + "\n")

    if (num_0 > len(net.nodes())/100 and num_0 > 10): print("WARNING: fitness.node_product(): " + str(num_0) + " nodes had 0 fitness out of " + str(len(net.nodes())))
    return fitness_score


def node_normz(net, denom):
    if (denom != 0):
        for n in net.nodes():
            net.node[n]['fitness'] /= float(denom)


def reset_fitness(net):
    for n in net.nodes():
        net.node[n]['fitness'] = 0


def reset_node_spins(net):
    for n in net.nodes():
        net.node[n]['up'] = 0
        net.node[n]['down'] = 0


