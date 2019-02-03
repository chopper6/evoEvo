import math, util

def calc_directed (net, node, fitness_metric, configs):

    num0, num1, prev_num0, prev_num1, output, prev_output =  calc_states(net, node, configs)

    if (num0 + num1 ==0): return 0 #poss need to add more conditions here

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

    elif (fitness_metric == 'None' or fitness_metric == 'none' or fitness_metric == 'error'):
        return 1

    else: assert(False) # unknown fitness metric




def calc_undirected (fitness_metric, net, node):
    # might be broken by now
    up, down = net.node[node]['up'], net.node[node]['down']

    if (up + down ==0): return 0

    if (fitness_metric == 'info'):
        return 1-entropy(up,down)

    elif (fitness_metric == 'info_normz'):

        base = math.pow(2,len(net.in_edges(node)) + len(net.out_edges(node)))
        I = 1-entropy_normz(up,down,base)
        bits = math.pow(base,I)/base
        if bits > 1 or bits < 0:
            print("\nBits fitness OOB = " + str(bits))
            print('from I = ' + str(I) + " and base = " + str(base) + "\n")
            #assert(False)
        return bits

    elif (fitness_metric == 'None' or fitness_metric == 'none'):
        return 1

    else: assert (False)  # unknown fitness metric



def entropy(num0,num1):
    total = num0 + num1

    if (num0 == 0): H0 = 0
    else: H0 = -1 * (num0 / float(total)) * math.log2(num0 / float(total))

    if (num1 == 0): H1 = 0
    else: H1 = -1 * (num1 / float(total)) * math.log2(num1 / float(total))

    return H0 + H1


def entropy_normz(num0,num1,base):
    total = num0 + num1

    if (num0 == 0): H0 = 0
    else: H0 = -1 * (num0 / float(total)) * math.log(num0 / float(total),base)

    if (num1 == 0): H1 = 0
    else: H1 = -1 * (num1 / float(total)) * math.log(num1 / float(total),base)

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



def calc_states(net, node, configs):
    num0, num1, prev_num0, prev_num1 = 0, 0, 0, 0
    feedfwd = util.boool(configs['feedforward'])
    if feedfwd: prev= 'prev_iteration_state'
    else: prev = 'prev_state'

    assert(configs['state_type'] == 'state_only')


    if net.node[node]['error']: #also add the ideal output as it is inputted to calc err (ie activate the node)
        if net.node[node]['ideal_output'] == 0: num0 += 1
        elif net.node[node]['ideal_output'] == 1: num1 += 1
        if net.node[node]['prev_ideal_output'] == 0: prev_num0 += 1
        elif net.node[node]['prev_ideal_output'] == 1: prev_num1 += 1


    for e in net.in_edges(node):
        if net.node[e[0]]['state'] == 0:  num0 += 1
        elif net.node[e[0]]['state'] == 1:   num1 += 1

        if net.node[e[0]][prev] == 0: prev_num0 += 1
        elif net.node[e[0]][prev] == 1:  prev_num1 += 1

    output = net.node[node]['state']
    prev_output = net.node[node][prev]

    if (num0 + num1 ==0): return 0

    return num0, num1, prev_num0, prev_num1, output, prev_output