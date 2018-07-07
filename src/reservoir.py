import math
from numpy.linalg import lstsq as np_leastsq


def step(net, configs):
    # TODO: explicitly debug this section

    apply_input(net, configs)
    step_fwd(net, configs)
    err = linear_reg(net, configs)

    lvl_1_learning(net, configs) #TODO: add this fn() and see if err decreases

    return err


def activation(net, node, configs):
    # curr linear activation with static bias (which is ~ thresh)
    # could add a few diff activation fns()
    # tech should exclude input_nodes, but shouldn't matter

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

    # threshold comparison
    if sum > 0: return 1
    else: return 0


def apply_input(net, configs):

    input_states = 'control'
    # later change to a config

    if input_states == 'control':
        for input_node in net.graph['input_nodes']:
            net.node[input_node]['state'] = 1
            assert(not net.in_edges(input_node))

def lvl_1_learning(net, configs):

    # TODO: add this
    return

    #learning = configs['lvl_1_learning']
    # can be greedy, naive_EA, or none


def linear_reg(net, configs):

    ideal_outputs = 'control'
    err = 0

    for output_node in net.graph['output_nodes']:
        if net.node[output_node]['state'] == None:
            # input hasn't reached output yet
            return None

        if ideal_outputs == 'control':
            assert(not net.out_edges(output_node))
            target = 1

        # calc least squares solution
        x = [net.node[in_edge[0]]['state'] for in_edge in net.in_edges(output_node)]
        w_soln = np_leastsq(x,target)
        sum = 0
        for i in range(len(x)):
            sum += x[i]*w_soln[i]
        err += math.pow(sum-target, 2)

    err /= len(net.graph['output_nodes'])
    return err


def step_fwd(net, configs):

    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']
    for n in net.nodes():
        net.node[n]['state'] = activation(net, n, configs)
