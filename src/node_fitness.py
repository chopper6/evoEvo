import math, util

def calc_discrete_directed (net, node, fitness_metric, configs, ideal_output = False):
    num0, num1, prev_num0, prev_num1 = 0, 0, 0, 0
    feedfwd = util.boool(configs['feedforward'])

    if ideal_output:
        assert(feedfwd) #TODO: otherwise prev_iteration_state --> prev_state
        output_node = net.graph['output_nodes'][node] #node is just used as an index

        if net.node[output_node]['state'] == 0: num0 += 1
        elif net.node[output_node]['state'] == 1: num1 += 1

        if net.node[output_node]['prev_iteration_state'] == 0: prev_num0 += 1
        elif net.node[output_node]['prev_iteration_state'] == 1: prev_num1 +=1

        output = net.graph['output'][node] #again, this is messy, but node is just the index
        prev_output = net.graph['prev_output'][node]


    else:
        for e in net.in_edges(node):
            if net.node[e[0]]['state'] == 0:  num0 += 1
            elif net.node[e[0]]['state'] == 1:   num1 += 1

            if feedfwd:
                if net.node[e[0]]['prev_iteration_state'] == 0: prev_num0 += 1
                elif net.node[e[0]]['prev_iteration_state'] == 1:  prev_num1 += 1
            else:
                if net.node[e[0]]['prev_state'] == 0: prev_num0 += 1
                elif net.node[e[0]]['prev_state'] == 1:  prev_num1 += 1


        output = net.node[node]['state']
        prev_output = net.node[node]['state']

    if (num0 + num1 ==0): return 0

    elif (fitness_metric == 'undirected_info'):
        return 1-entropy(num0,num1)

    elif (fitness_metric == 'directed_info'):
        info = entropy(num0,num1) - cond_entropy(num0, num1, output)
        assert(info <= 1 and info >= 0)
        return info

    elif (fitness_metric == 'predictive_info'):
        predictive_info = entropy(num0,num1) - cond_entropy(num0, num1, prev_output)
        assert(predictive_info <= 1 and predictive_info >= 0)
        return predictive_info

    elif (fitness_metric == 'flux_info'):
        # flux = (info - predictive_info); should be min'd
        # based on Still et al. Thermodynamics of Prediction
        prev_info = entropy(prev_num0,prev_num1) - cond_entropy(prev_num0, prev_num1, prev_output)
        predictive_info = entropy(num0,num1) - cond_entropy(num0, num1, prev_output)
        flux = prev_info - predictive_info
        assert(flux <= 1 and flux >= 0)
        return flux

    elif (fitness_metric == 'None' or fitness_metric == 'none'):
        return 1

    else: assert(False) # unknown fitness metric


def calc_discrete_undirected (fitness_metric, up, down):
    # might be broken by now
    if (up + down ==0): return 0

    if (fitness_metric == 'info'):
        return 1-entropy(up,down)

    elif (fitness_metric == 'None' or fitness_metric == 'none'):
        return 1

    else: assert (False)  # unknown fitness metric



def calc_continuous (net, node, fitness_metric, configs, distrib_lng=1, ideal_output = False):
    if net.node[node]['layer'] == 'input': return None
    feedfwd = util.boool(configs['feedforward'])

    inputs, prev_inputs, output, prev_output = retrieve_states(net, node, ideal_output, feedfwd)

    if len(inputs)==0: return None

    mean, var, entropish, cond_entropish = None, None, None, None #those annoying ass warnings...
    if (fitness_metric != 'predictive_info' and fitness_metric != 'flux_info'): mean, var, entropish, cond_entropish  = calc_continuous_features(inputs, output, distrib_lng)

    if (fitness_metric == 'entropish'):
        return entropish

    elif (fitness_metric == 'variance'):
        fitness = var
        return fitness

    elif (fitness_metric == 'undirected_info'):
        info = 1-entropish
        assert(info >= 0 and info <= 1)
        return info

    elif (fitness_metric == 'directed_info'):
        info = entropish - cond_entropish
        assert(info >= 0 and info <= 1)
        return info

    elif (fitness_metric == 'predictive_info'):

        mean, var, entropish, predictive_cond_entropish = calc_continuous_features(inputs, prev_output, distrib_lng)

        predictive_info = entropish - predictive_cond_entropish
        assert(predictive_info >= 0 and predictive_info <= 1)
        return predictive_info

    elif (fitness_metric == 'flux_info'):
        #TODO: not sure why but predictive_info always = prev_info
        # poss a problem related to the base problem?

        prev_mean, prev_var, prev_entropish, prev_cond_entropish = calc_continuous_features(prev_inputs, prev_output, distrib_lng)
        mean, var, entropish, predictive_cond_entropish = calc_continuous_features(inputs, prev_output, distrib_lng)

        predictive_info = entropish - predictive_cond_entropish
        prev_info = prev_entropish - prev_cond_entropish
        flux = prev_info - predictive_info
        assert(flux >= 0 and flux <= 1)
        return flux


    elif (fitness_metric == 'entropish_old'):
        if (var < .01): entropish = 0
        else: entropish = 1/math.pow(math.e, 1/var)
        fitness = 1 - entropish
        assert(fitness >= 0 and fitness <= 1)
        return fitness

    elif (fitness_metric == 'None' or fitness_metric == 'none'):
        return 1

    assert(False) #unknown fitness metric/shouldn't get here



def entropy(num0,num1):
    total = num0 + num1

    if (num0 == 0): H0 = 0
    else: H0 = -1 * (num0 / float(total)) * math.log2(num0 / float(total))

    if (num1 == 0): H1 = 0
    else: H1 = -1 * (num1 / float(total)) * math.log2(num1 / float(total))

    return H0 + H1



def cond_entropy(num0,num1,given):
    total = num0 + num1

    if (given==1): #the unexpected part are the opposite states
        if (num0 == 0): H0 = 0
        else: H0 = -1 * (num0 / float(total)) * math.log2(num0 / float(total))
        return H0

    if (given==0):
        if (num1 == 0): H1 = 0
        else: H1 = -1 * (num1 / float(total)) * math.log2(num1 / float(total))
        return H1

    else:
        print("ERROR in node_fitness.conditional_entropy(): given state = " + str(given))
        assert(False)



def retrieve_states(net, node, ideal_output, feedfwd):
    inputs, prev_inputs = [], []
    if feedfwd: prev = 'prev_iteration_state'
    else: prev = 'prev_state'

    if ideal_output: #used for fitness based on ideal_output of base problem
        # then node is just an index (ugly i know)
        output_node = net.graph['output_nodes'][node]
        inputs.append(net.node[output_node]['state'])
        prev_inputs.append(net.node[output_node][prev])

        output = net.graph['output'][node]  # again, this is messy, but node is just the index
        prev_output = net.graph['prev_output'][node]

    else:
        inputs, prev_inputs = [], []
        for in_edge in net.in_edges(node):
            if net.node[in_edge[0]]['state'] is not None:
                inputs.append(net.node[in_edge[0]]['state'])

            if net.node[in_edge[0]][prev] is not None:
                prev_inputs.append(net.node[in_edge[0]][prev])

        output = net.node[node]['state']
        prev_output = net.node[node][prev]

    return  inputs, prev_inputs, output, prev_output


def calc_continuous_features(inputs, output, distrib_lng):
    if len(inputs)==0 or inputs is None: assert(False) #this case should already be handled higher up

    var, entropish, cond_entropish = 0, 0, 0
    mean = sum(inputs)/float(len(inputs))

    for input in inputs:
        var += math.pow((mean-input),2)
        pr = 1-abs(mean-input)/ float(distrib_lng)
        assert(pr >= 0 and pr <= 1)
        if pr != 0:
            entropish -= math.log2(pr)
            cond_entropish -= math.log2(pr)*abs(input-output)

    if (len(inputs) > 1): var /= len(inputs) - 1
    entropish /= len(inputs)
    cond_entropish /= len(inputs)

    return mean, var, entropish, cond_entropish