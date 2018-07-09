import math, random as rd


def step(net, configs):
    # TODO: explicitly debug this section

    input, output = problem_instance(net, configs)
    apply_input(net, input)
    step_fwd(net, configs)
    MSE = stochastic_backprop (net, configs, output)
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE


def activation(net, node, configs):
    # curr linear activation with static bias (which is ~ thresh)
    # could add a few diff activation fns()
    # tech should exclude input_nodes, but shouldn't matter

    activation_fn = configs['activation_function']

    # curr 2nd gen neurons

    sum = 0
    num_active = 0
    for edge in net.in_edges(node):
        #use previous state, since state is reserved for the new iteration
        if net.node[edge[0]]['prev_state'] != None:
            edge_val = net.node[edge[0]]['prev_state'] * net[edge[0]][edge[1]]['weight']
            assert(edge_val >= -1 and edge_val <= 1)     # assumes weights in [-1,1]
            sum += edge_val
            num_active += 1
        sum += net.node[node]['neuron_bias']

    #if num_active > 0: sum /= num_active #don't normalize like this, since will always be < 1
    if num_active == 0: return None
    # does bias should take care of this?????????

    if activation_fn == 'linear':
        # threshold comparison
        if sum > 0: return 1
        else: return 0

    elif activation_fn == 'sigmoid':
        return 1/(1+math.exp(-(sum)))

    else: assert(False)

def apply_input(net, input):

    sorted_input_nodes = sorted(net.graph['input_nodes'])
    assert(len(sorted_input_nodes) == len(input))

    for i in range(len(sorted_input_nodes)):
        net.node[sorted_input_nodes[i]]['state'] = input[i]


def lvl_1_reservoir_learning(net, configs):

    # TODO: add this
    return

    #learning = configs['lvl_1_learning']
    # can be greedy, naive_EA, or none


def problem_instance(net, configs):

    base_problem = configs['base_problem']
    input, output = [],[]

    if base_problem  == 'control':
        for input_node in net.graph['input_nodes']:
            input.append(1)
            assert(not net.in_edges(input_node))
        for i in range(len(net.graph['output_nodes'])):
            output.append(1)

    elif base_problem  == 'control00':
        for input_node in net.graph['input_nodes']:
            input.append(0)
            assert(not net.in_edges(input_node))
        for i in range(len(net.graph['output_nodes'])):
            output.append(0)

    elif base_problem  == 'control10':
        for input_node in net.graph['input_nodes']:
            input.append(1)
            assert(not net.in_edges(input_node))
        for i in range(len(net.graph['output_nodes'])):
            output.append(0)

    elif base_problem == 'control01':
        for input_node in net.graph['input_nodes']:
            input.append(0)
            assert (not net.in_edges(input_node))
        for i in range(len(net.graph['output_nodes'])):
            output.append(1)


    elif base_problem  == 'XOR':
        assert(len(net.graph['input_nodes']) == 2)
        assert(len(net.graph['output_nodes']) == 1)

        input.append(rd.choice([0,1]))
        input.append(rd.choice([0,1]))

        if (input[0] == 1 and input[1] == 0):     output.append(1)
        elif (input[0] == 0 and input[1] == 1):   output.append(1)
        else:                                     output.append(0)

    elif base_problem  == 'meanAF':
        for i in range(len(net.graph['input_nodes'])):
            input.append(rd.choice([0,1]))
        for i in range(len(net.graph['output_nodes'])):
            input.append(rd.choice([0,1]))

    else: assert(False)

    return input, output


def stochastic_backprop(net, configs, ideal_output):

    learning_rate = float(configs['learning_rate'])
    assert(configs['activation_function'] == 'sigmoid')
    MSE  = 0

    sorted_output_nodes = sorted(net.graph['output_nodes']) #fn doesn't matter as long as its consistent
    i = 0
    num_active_outputs = len(sorted_output_nodes)
    for output_node in sorted_output_nodes:

        if net.node[output_node]['state'] != None:
            # input hasn't reached all outputs yet
            #return None --> now correct what is available

            output = net.node[output_node]['state']
            err = math.pow(ideal_output[i]-output,2)
            print("\nOutput Node = " + str(output) + ", resulting in err = " + str(err))
            MSE += err
            #print('\nbackprop(): output of node = ' + str(output) + ", with err " + str(err))

            # assumes sigmoid
            delta = (ideal_output[i]-output)*output*(1-output)
            for in_edge in net.in_edges(output_node):
                if net.node[in_edge[0]]['state']:
                    weight_contribution = net.node[in_edge[0]]['state'] #*net[in_edge[0]][in_edge[1]]['weight']
                    partial_err = delta * weight_contribution
                    print("delta = " + str(delta) + ", weight_contrib = " + str(weight_contribution) + ", curr_weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))
                    net[in_edge[0]][in_edge[1]]['weight'] += partial_err*learning_rate
                    print("now weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))

            # calc for bias
            partial_err = delta * net.node[output_node]['neuron_bias']
            print("old bias = " + str(net.node[output_node]['neuron_bias']) + ", its err contrib = " + str(partial_err))
            net.node[output_node]['neuron_bias'] -= partial_err*learning_rate
            print("new bias = " + str(net.node[output_node]['neuron_bias']))

        else: num_active_outputs -= 1

    if num_active_outputs == 0: return None

    if (num_active_outputs >0):
        MSE /= 2*num_active_outputs
        print("\nReturning MSE of " + str(MSE) + " with " + str(num_active_outputs) + " active outputs.\n")
    return MSE


def step_fwd(net, configs):

    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']
    for n in net.nodes():
        net.node[n]['state'] = activation(net, n, configs)
