import math
from numpy.linalg import lstsq as np_leastsq
import numpy as np


def step(net, configs):
    # TODO: explicitly debug this section

    apply_input(net, configs)
    step_fwd(net, configs)
    MSE = stochastic_backprop (net, configs)
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE


def activation(net, node, configs):
    # curr linear activation with static bias (which is ~ thresh)
    # could add a few diff activation fns()
    # tech should exclude input_nodes, but shouldn't matter

    activation_fn = configs['activation_function']

    # curr 2nd gen neurons

    sum, num_active = 0, 0
    for edge in net.in_edges(node):
        #use previous state, since state is reserved for the new iteration
        if net.node[edge[0]]['prev_state'] != None:
            edge_val = net.node[edge[0]]['prev_state'] * net[edge[0]][edge[1]]['weight']
            assert(edge_val >= -1 and edge_val <= 1)     # assumes weights in [-1,1]
            sum += edge_val
            num_active += 1

    #if num_active > 0: sum /= num_active #don't normalize like this, since will always be < 1
    if num_active == 0: return None

    if activation_fn == 'linear':
        # threshold comparison
        if sum > 0: return 1
        else: return 0

    elif activation_fn == 'sigmoid':
        return 1/(1+math.exp(-(sum)))

    else: assert(False)

def apply_input(net, configs):

    base_problem = configs['base_problem']

    if base_problem  == 'control':
        for input_node in net.graph['input_nodes']:
            net.node[input_node]['state'] = 1
            assert(not net.in_edges(input_node))

    else: assert(False)


def lvl_1_reservoir_learning(net, configs):

    # TODO: add this
    return

    #learning = configs['lvl_1_learning']
    # can be greedy, naive_EA, or none

def stochastic_backprop(net, configs):

    base_problem = configs['base_problem']
    learning_rate = float(configs['learning_rate'])

    MSE, targets = 0, None #targets just bc of annoying ass warnings

    if base_problem == 'control':
        targets = [1 for i in range(len(net.graph['output_nodes']))]
    else: assert(False)

    sorted_output_nodes = sorted(net.graph['output_nodes']) #fn doesn't matter as long as its consistent
    i = 0
    num_active_outputs = len(sorted_output_nodes)
    for output_node in sorted_output_nodes:
        assert (not net.out_edges(output_node))

        if net.node[output_node]['state'] != None:
            # input hasn't reached all outputs yet
            #return None --> now correct what is available

            output = net.node[output_node]['state']
            err = math.pow(targets[i]-output,2)
            MSE += err
            #print('\nbackprop(): output of node = ' + str(output) + ", with err " + str(err))

            # assumes sigmoid
            # TODO: add bias
            delta = (targets[i]-output)*output*(1-output)
            for in_edge in net.in_edges(output_node):
                if net.node[in_edge[0]]['state']:
                    weight_contribution = net.node[in_edge[0]]['state']*net[in_edge[0]][in_edge[1]]['weight']
                    partial_err = delta * weight_contribution
                    #print("delta = " + str(delta) + ", weight_contrib = " + str(weight_contribution) + ", curr_weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))
                    net[in_edge[0]][in_edge[1]]['weight'] -= partial_err*learning_rate
                    #print("now weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))

        else: num_active_outputs -= 1

    if (num_active_outputs >0): MSE /= 2*num_active_outputs
    return MSE


def step_fwd(net, configs):

    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']
    for n in net.nodes():
        net.node[n]['state'] = activation(net, n, configs)
