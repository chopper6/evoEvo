import math
from operator import attrgetter
import node_fitness, util

def eval_fitness(population, fitness_direction):
    #determines fitness of each individual and orders the population by fitness
    if (fitness_direction == 'max'): population = sorted(population,key=attrgetter('fitness'), reverse=True)
    elif (fitness_direction == 'min'):  population = sorted(population,key=attrgetter('fitness'))
    else: print("ERROR in fitness.eval_fitness(): unknown fitness_direction " + str(fitness_direction) + ", population not sorted.")

    return population

def calc_node_fitness(net, configs):
    directed = util.boool(configs['directed'])
    fitness_metric = str(configs['fitness_metric'])
    interval = configs['interval']

    if interval == 'discrete':
        if directed:
            for n in net.nodes():
                up_in, up_out, down_in, down_out = net.node[n]['up_in'], net.node[n]['up_out'], net.node[n]['down_in'], net.node[n]['down_out']
                net.node[n]['fitness'] += node_fitness.calc_directed(fitness_metric, up_in, up_out, down_in, down_out)

        else:
            for n in net.nodes():
                up, down = net.node[n]['up'], net.node[n]['down']
                net.node[n]['fitness'] += node_fitness.calc_undirected(fitness_metric, up,down)


    elif interval == 'continuous':
        assert(not directed)
        temp_switch = configs['temp_switch']

        for n in net.nodes():
            states = []
            for in_edge in net.in_edges(n):
                if net[in_edge[0]][in_edge[1]]['state'] is not None:
                    states.append(net[in_edge[0]][in_edge[1]]['state'])
            for out_edge in net.out_edges(n):
                if net[out_edge[0]][out_edge[1]]['state'] is not None:
                    states.append(net[out_edge[0]][out_edge[1]]['state'])

            info, var = node_fitness.calc_continuous(states, temp_switch)
            net.node[n]['fitness'] += info
            net.node[n]['var'] += var

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


def node_normz(net, denom, configs):
    interval = configs['interval']
    if (denom != 0):
        for n in net.nodes():
            net.node[n]['fitness'] /= float(denom)
            if (interval == 'continuous'): net.node[n]['var'] /= float(denom)


def reset_node_fitness(net, configs):
    interval = configs['interval']

    for n in net.nodes():
        net.node[n]['fitness'] = 0
        if (interval=='continuous'): net.node[n]['var'] = 0



