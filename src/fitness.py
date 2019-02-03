import math
import node_fitness_discrete, node_fitness_continuous, util

def eval_fitness(population, fitness_direction, fitness_metric):
    #determines fitness of each individual and orders the population by fitness

    #if fitness_metric=='error' or fitness_metric == 'Error': reverse = False
    #else: reverse = True  # MAKING FITNESS A -PRODUCT OF NODES ACTUALLY INVERTS THE MAX/MIN VALUE OF NET RELATIVE TO ITS NODES

    reverse = False #TODO: may fuck up earlier models, but just too confusing otherwise

    if (reverse and fitness_direction == 'min') or (not reverse and fitness_direction == 'max'): direction = 'max'
    else: direction = 'min'

    assert(fitness_direction == 'min' or fitness_direction == 'max')

    if (direction == 'max'): population = sorted(population,key=fitness_key, reverse=True)
    elif (direction == 'min'):  population = sorted(population,key=fitness_key)
    #else: print("ERROR in fitness.eval_fitness(): unknown fitness_direction " + str(fitness_direction) + ", population not sorted.")

    #temp for debug purposes
    #print("\nIn fitness line 11: order of " + str(fitness_direction) + " sorted population:")
    #for p in population:
    #    print(p.graph['fitness'])
    if (len(population) > 1):

        if (direction == 'min'): assert(population[0].graph['fitness'] <= population[1].graph['fitness'] )
        elif (direction == 'max'): assert(population[0].graph['fitness'] >= population[1].graph['fitness'] )
    #print("\n")

    return population



def fitness_key(net):
    return net.graph['fitness']


def calc_node_fitness(net, configs):
    directed = util.boool(configs['directed'])
    fitness_metric = str(configs['fitness_metric'])
    interval = configs['interval']
    debug = configs['debug']

    if (fitness_metric == 'error'):
        return #calc at net lvl

    if interval == 'discrete':
        #if debug: print("WARNING: discrete fitness likely needs a lotto debugging!")
        if directed:
            for n in net.nodes():
                if net.node[n]['layer'] != 'input':
                    net.node[n]['fitness'] += node_fitness_discrete.calc_directed(net, n, fitness_metric, configs)

        else:
            #assert(False) #i may have screwed this up, not sure what # up and down refer to anymore...
            for n in net.nodes():
                net.node[n]['fitness'] += node_fitness_discrete.calc_undirected(fitness_metric,net, n)


    elif interval == 'continuous':

        if directed:
            curr_fitness = 1
            for n in net.nodes():
                fitness = node_fitness_continuous.calc(net, n, fitness_metric, configs)
                if fitness is not None: #for ex input nodes or nodes with no inputs will yield none
                    net.node[n]['fitness'] += fitness
                    if fitness != 0: curr_fitness += -1*math.log(net.node[n]['fitness'])
            return curr_fitness


        else:
            assert(False) #needs a whole bunch of debugging
            for n in net.nodes():
                states = []
                for in_edge in net.in_edges(n):
                    if net[in_edge[0]][in_edge[1]]['state'] is not None:
                        states.append(net[in_edge[0]][in_edge[1]]['state'])
                for out_edge in net.out_edges(n):
                    if net[out_edge[0]][out_edge[1]]['state'] is not None:
                        states.append(net[out_edge[0]][out_edge[1]]['state'])

                fitness = node_fitness_continuous.calc(states, fitness_metric)
                if fitness is not None: net.node[n]['fitness'] += fitness


def node_product(net, scale_node_fitness, configs):

    if configs['fitness_metric'] == 'error': return net.graph['error']
    elif configs['fitness_metric'] == 'None': return 0

    fitness_score = 0
    num_0 = 0
    num_under, num_over = 0,0

    base = math.pow(2, len(net.in_edges()) + len(net.out_edges()))

    for n in net.nodes():
        if net.node[n]['fitness'] == 0:
            num_0 += 1
        else:
            if scale_node_fitness: #hasn't really worked so far, in progress
                num_edges = len(net.edges(n))
                Inode = net.node[n]['fitness']
                fitness_score += -1*math.log(net.node[n]['fitness'], base)
                # SHOULD AVOID INVERSION THIS WAY
            else:
                # NOTE THAT THIS SEEMS TO INVERT THE MEANING, IE INFO --> ENTROPY : MAX --> MIN
                fitness_score += -1*math.log(net.node[n]['fitness'])


    if (num_over != 0 or num_under != 0):
        print("# I < 0 = " + str(num_under) + "\t # I > 1 = " + str(num_over) + "\n")

    if util.boool(configs['debug']):
        if (num_0 > len(net.nodes())/100 and num_0 > 10): print("WARNING: fitness.node_product(): " + str(num_0) + " nodes had 0 fitness out of " + str(len(net.nodes())))

    if scale_node_fitness:
        fitness_score = 1-fitness_score #change from entropy to info
        if fitness_score > 1 or fitness_score < 0:
            print("Total net fitness before adjustment = " + str(fitness_score))
            assert(False)
        fitness_score = math.pow(base,fitness_score) #/base
        if fitness_score > 1 or fitness_score < 0:
            print("Total net fitness OOB = " + str(fitness_score))
            assert(False)

    return fitness_score


def node_normz(net, denom, configs):
    if (denom != 0):
        for n in net.nodes():
            net.node[n]['fitness'] /= float(denom)

    net.graph['output_fitness'] /= float(denom)

def reset_nodes(net, configs):
    for n in net.nodes():
        net.node[n]['fitness'] = 0

    if  util.boool(configs['feedforward']) and util.boool(configs['directed']):
        for n in net.nodes():
            net.node[n]['state'] = None

    net.graph['output_fitness'] = 0


