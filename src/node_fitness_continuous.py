import math, util

def calc (net, node, fitness_metric, configs):
    if net.node[node]['layer'] == 'input': return None
    distrib_lng = calc_distrib_lng(configs['activation_function'])


    if (fitness_metric == 'None' or fitness_metric == 'none' or fitness_metric == 'error'):
        return 0

    inputs, prev_inputs, output, prev_output = retrieve_states(net, node, configs)

    if len(inputs)==0: return None

    mean, var, entropish, cond_entropish = None, None, None, None #those annoying ass warnings...
    if (fitness_metric != 'predictive_info' and fitness_metric != 'flux_info'): mean, var, entropish, cond_entropish  = calc_features(inputs, output, configs)

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
        #info = entropish - cond_entropish
        info = 1 - cond_entropish
        assert(info >= 0 and info <= 1)
        return info

    elif (fitness_metric == 'predictive_info'):

        if prev_output is None: return None
        mean, var, entropish, predictive_cond_entropish = calc_features(inputs, prev_output, configs)

        predictive_info = 1 - predictive_cond_entropish
        #predictive_info = entropish - predictive_cond_entropish
        assert(predictive_info >= 0 and predictive_info <= 1)
        return predictive_info

    elif (fitness_metric == 'flux_info'):
        # poss a problem related to the base problem?

        if prev_output is None or prev_inputs is None or len(prev_inputs)==0: return None

        prev_mean, prev_var, prev_entropish, prev_cond_entropish = calc_features(prev_inputs, prev_output, configs)
        mean, var, entropish, predictive_cond_entropish = calc_features(inputs, prev_output, configs)

        #predictive_info = entropish - predictive_cond_entropish
        #prev_info = prev_entropish - prev_cond_entropish

        predictive_info = 1 - predictive_cond_entropish
        prev_info = 1 - prev_cond_entropish
        flux = prev_info - predictive_info
        assert(flux >= 0 and flux <= 1)
        return flux

    elif (fitness_metric == 'flux_info_positive'):
        # poss a problem related to the base problem?

        if prev_output is None or prev_inputs is None or len(prev_inputs)==0: return None

        prev_mean, prev_var, prev_entropish, prev_cond_entropish = calc_features(prev_inputs, prev_output, configs)
        mean, var, entropish, predictive_cond_entropish = calc_features(inputs, prev_output, configs)

        #predictive_info = entropish - predictive_cond_entropish
        #prev_info = prev_entropish - prev_cond_entropish

        predictive_info = 1 - predictive_cond_entropish
        prev_info = 1 - prev_cond_entropish
        flux = prev_info - predictive_info
        if flux<0:  flux = 0
        assert(flux >= 0 and flux <= 1)
        return flux

    elif (fitness_metric == 'flux_info_abs'):
        # poss a problem related to the base problem?

        if prev_output is None or prev_inputs is None or len(prev_inputs)==0: return None

        prev_mean, prev_var, prev_entropish, prev_cond_entropish = calc_features(prev_inputs, prev_output, configs)
        mean, var, entropish, predictive_cond_entropish = calc_features(inputs, prev_output, configs)

        #predictive_info = entropish - predictive_cond_entropish
        #prev_info = prev_entropish - prev_cond_entropish

        predictive_info = 1 - predictive_cond_entropish
        prev_info = 1 - prev_cond_entropish
        flux = abs(prev_info - predictive_info)
        assert(flux >= 0 and flux <= 1)
        return flux



    elif (fitness_metric == 'entropish_old'):
        if (var < .01): entropish = 0
        else: entropish = 1/math.pow(math.e, 1/var)
        fitness = 1 - entropish
        assert(fitness >= 0 and fitness <= 1)
        return fitness


    assert(False) #unknown fitness metric/shouldn't get here



def retrieve_states(net, node, configs):
    #TODO: double debug this bit

    inputs, prev_inputs = [], []
    feedfwd = util.boool(configs['feedforward'])
    state_type = configs['state_type']
    include_bias_state = util.boool(configs['include_bias_state'])

    if feedfwd: prev = 'prev_iteration_state'
    else: prev = 'prev_state'

    if net.node[node]['layer'] == 'error': #also add the ideal output as it is inputted to calc err (ie activate the node)
        inputs.append(net.node[node]['ideal_output'])
        if net.node[node]['prev_ideal_output'] is not None: prev_inputs.append(net.node[node]['prev_ideal_output'])

    inputs, prev_inputs = [], []
    for in_edge in net.in_edges(node):
        if net.node[in_edge[0]]['state'] is not None:
            if state_type=='state_only': inputs.append(net.node[in_edge[0]]['state'])
            elif state_type=='weighted':  inputs.append(net.node[in_edge[0]]['state']*net[in_edge[0]][in_edge[1]]['weight'])
            elif state_type=='weight_sign':  inputs.append(net.node[in_edge[0]]['state']*sgn(net[in_edge[0]][in_edge[1]]['weight']))
            else: assert(False)

        if net.node[in_edge[0]][prev] is not None:
            if state_type == 'state_only':
                prev_inputs.append(net.node[in_edge[0]][prev])
            elif state_type == 'weighted':
                prev_inputs.append(net.node[in_edge[0]][prev] * net[in_edge[0]][in_edge[1]]['prev_weight'])
            elif state_type == 'weight_sign':
                prev_inputs.append(net.node[in_edge[0]][prev] * sgn(net[in_edge[0]][in_edge[1]]['prev_weight']))


    if include_bias_state:
        inputs.append(net.node[node]['neuron_bias'])
        prev_inputs.append(net.node[node]['prev_neuron_bias'])

    output = net.node[node]['state']
    prev_output = net.node[node][prev]

    return  inputs, prev_inputs, output, prev_output


def calc_features(inputs, output, configs):
    if len(inputs)==0 or inputs is None: assert(False) #this case should already be handled higher up
    entropish_factor = configs['entropish_factor']
    distrib_lng = calc_distrib_lng(configs['activation_function'])

    var, entropish, cond_entropish = 0, 0, 0
    if output is None: cond_entropish = None
    mean = sum(inputs)/float(len(inputs))

    for input in inputs:
        var += math.pow((mean-input),2)
        if entropish_factor == 'abs': pr = 1-abs(mean-input)/ float(distrib_lng)
        elif entropish_factor == 'sq' or entropish_factor == 'squared': pr = 1-math.pow(abs(mean-input)/ float(distrib_lng),2)
        else: assert(False)

        assert(pr >= 0 and pr <= 1)
        if pr != 0:
            entropish -= math.log2(pr)
            if output is not None:
                cond_weight = abs(input-output)/float(distrib_lng)
                if entropish_factor == 'sq' or entropish_factor=='squared': cond_weight = math.pow(cond_weight,2)
                cond_entropish -= math.log2(pr)*cond_weight

    if (len(inputs) > 1): var /= len(inputs) - 1
    entropish /= len(inputs)
    if output is not None: cond_entropish /= len(inputs)

    return mean, var, entropish, cond_entropish




def calc_distrib_lng(actvn_fn):
    if actvn_fn == 'sigmoid':
        distrib_lng = 1
    elif actvn_fn == 'tanh':
        distrib_lng = 2
    else:
        assert (False)

    return distrib_lng


def sgn(val):
    if val < 0: return -1
    elif val > 0: return 1
    else: return 0
