import math
from numpy.linalg import lstsq as np_leastsq


def step(net, configs):
    # TODO: explicitly debug this section

    apply_input(net, configs)
    step_fwd(net, configs)
    outputs = receive_output(net)

    return outputs


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


def linear_reg(net, outputs, configs):

    ideal_outputs = 'control' #later as param
    err = 0
    targets = None #those annoying errors

    if ideal_outputs == 'control':
        targets = [1 for i in range(len(net.graph['output_nodes']))]
        print(net.graph['output_nodes'])
    else: assert(False)

    print("\nreservoir.linear_reg:\n")
    print("outputs = " + str(outputs))
    print("targets = " + str(targets) + "\n")

    # calc least squares solution
    w_soln = np_leastsq(outputs,targets)
    #assert(len(w_soln) == len(net.graph['output_nodes']))

    print("lin reg output = " + str(w_soln))
    '''
    sum = 0
    for i in range(len(outputs)):
        for j
        sum += x[i]*w_soln[i]
    err += math.pow(sum-target, 2)

    err /= len(net.graph['output_nodes'])
    '''
    return err


def receive_output(net):

    outputs = [None for i in range(len(net.graph['output_nodes']))]
    sorted_output_nodes = sorted(net.graph['output_nodes']) #fn doesn't matter as long as its ocnsistent
    i = 0
    for output_node in sorted_output_nodes:
        assert (not net.out_edges(output_node))

        if net.node[output_node]['state'] == None:
            # input hasn't reached all outputs yet
            return None

        outputs[i] = [net.node[in_edge[0]]['state'] for in_edge in net.in_edges(output_node)]
        print('receive_output outputs = ' + str(outputs[i]))

    if len(outputs)==1: outputs = outputs[0]
    return outputs

def step_fwd(net, configs):

    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']
    for n in net.nodes():
        net.node[n]['state'] = activation(net, n, configs)
