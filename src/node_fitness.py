import math

def calc_discrete_directed (net, node, fitness_metric):
    num0, num1 = 0, 0

    for e in net.in_edges(node):
        if net.node[e[0]]['state'] == 0: num0 += 1
        elif net.node[e[0]]['state'] == 1: num1 += 1

    if (num0 + num1 ==0): return 0

    elif (fitness_metric == 'info'):
        return 1-shannon_entropy(num0,num1)

    else: assert(False) # unknown fitness metric


def calc_discrete_undirected (fitness_metric, up, down):
    if (up + down ==0): return 0

    if (fitness_metric == 'info'):
        return 1-shannon_entropy(up,down)

    else: assert (False)  # unknown fitness metric


def calc_continuous (states, fitness_metric, distrib_lng=1):
    if len(states)==0: 
        fitness = 1
        return fitness

    mean = sum(states)/len(states)
    var, entropish = 0, 0
    # may have to change distrib_lng if, for ex. states can be in [-1,1]

    for state in states:
        var += math.pow((mean-state),2)
        pr = 1-abs(mean-state)/ float(distrib_lng)
        assert(pr >= 0 and pr <= 1)
        if pr != 0:
            entropish -= math.log2(pr)

    if (len(states) > 1): var /= len(states) - 1
    if (len(states) > 0): entropish /= len(states)

    if var == 0:
        fitness = 1
        return fitness

    fitness = None

    if (fitness_metric == 'entropish'):
        return entropish

    elif (fitness_metric == 'variance'):
        fitness = var

    elif (fitness_metric == 'entropish_old'):
        if (var < .01): entropish = 0
        else: entropish = 1/math.pow(math.e, 1/var)
        fitness = 1 - entropish
        assert(fitness >= 0 and fitness <= 1)

    else: assert(False) #unknown fitness metric

    return fitness


def shannon_entropy(up,down):
    if (up == 0): H_up = 0
    else: H_up = -1 * (up / (up + down)) * math.log2(up / float(up + down))

    if (down == 0):  H_down = 0
    else:  H_down = -1 * (down / (up + down)) * math.log2(down / float(up + down))

    return H_up + H_down
