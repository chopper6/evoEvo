import math, random as rd, networkx as nx, numpy as np
import util


def step(net, configs):

    input, output = problem_instance(net, configs)
    apply_input(net, input)
    step_fwd(net, configs)
    MSE = stochastic_backprop (net, configs, output)
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE

def feedfwd_step(net, configs):
    # possibly make this the more general model?

    input, output = problem_instance(net, configs)
    apply_input(net, input)
    diameter = nx.diameter(net.to_undirected())
    for i in range(diameter): #all nodes should have had a chance to effect one another (except for directed aspect...)
        step_fwd(net, configs)
    save_states(net, configs)
    MSE = stochastic_backprop (net, configs, output) #i.e. only care about last iteration
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE, output



def activation(net, node, configs):
    # curr linear activation with static bias (which is ~ thresh)
    # could add a few diff activation fns()
    # tech should exclude input_nodes, but shouldn't matter

    activation_fn = configs['activation_function']

    # curr 2nd gen neurons

    sum = 0
    num_active = 0
    for edge in net.in_edges(node):
        #use previous state, since state is reserved for the new iteration (see step_fwd())
        if (net.node[edge[0]]['prev_state'] is not None):
            edge_val = net.node[edge[0]]['prev_state'] * net[edge[0]][edge[1]]['weight']

            sum += edge_val
            num_active += 1
        sum += net.node[node]['neuron_bias']

    #if num_active > 0: sum /= num_active #don't normalize like this, since will always be < 1
    # if num_active == 0: return None
    # does bias should take care of this?????????

    if activation_fn == 'linear':
        # threshold comparison
        if sum > 0: return 1
        else: return 0

    elif activation_fn == 'sigmoid':
        return 1/(1+math.exp(-(sum)))

    elif activation_fn == 'tanh':
        return np.tanh(sum)

    else: assert(False)

def apply_input(net, input):

    sorted_input_nodes = sorted(net.graph['input_nodes'])
    assert(len(sorted_input_nodes) == len(input))

    for i in range(len(sorted_input_nodes)):
        net.node[sorted_input_nodes[i]]['state'] = input[i]


def lvl_1_reservoir_learning(net, configs):
    # alters weights in reservoir (as opposed to output layer)

    # TODO: add this
    return

    #learning = configs['lvl_1_learning']
    # can be greedy, naive_EA, or none


def problem_instance(net, configs):
    # returns input and output, as well as saving them (and their previous iteration) to the net

    base_problem = configs['base_problem']
    input, output = [],[]

    if base_problem  == 'control':
        for input_node in net.graph['input_nodes']:
            input.append(1)
            #if not util.boool(configs['in_edges_to_inputs']):
            assert(not net.in_edges(input_node))
        for i in range(len(net.graph['output_nodes'])):
            output.append(1)

    elif base_problem  == 'control00':
        for input_node in net.graph['input_nodes']:
            input.append(0)
        for i in range(len(net.graph['output_nodes'])):
            output.append(0)

    elif base_problem  == 'control10':
        for input_node in net.graph['input_nodes']:
            input.append(1)
        for i in range(len(net.graph['output_nodes'])):
            output.append(0)

    elif base_problem == 'control01':
        for input_node in net.graph['input_nodes']:
            input.append(0)
        for i in range(len(net.graph['output_nodes'])):
            output.append(1)

    # logic functions, should be used with sigmoid activation, since results in output in [0,1]
    elif base_problem == 'AND':
        assert(len(net.graph['input_nodes']) == 2)
        assert(len(net.graph['output_nodes']) == 1)
        input.append(rd.choice([0,1]))
        input.append(rd.choice([0,1]))

        if [input[0] == input[1]]:  output.append(1)
        else:                       output.append(0)

    elif base_problem == 'OR':
        assert(len(net.graph['input_nodes']) == 2)
        assert(len(net.graph['output_nodes']) == 1)
        input.append(rd.choice([0,1]))
        input.append(rd.choice([0,1]))

        if [input[0] == 1 or input[1] == 1]:    output.append(1)
        else:                                   output.append(0)

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

    if net.graph['input'] is not None: net.graph['prev_input'] = net.graph['input']
    if net.graph['output'] is not None: net.graph['prev_output'] = net.graph['output']
    net.graph['input'] = input
    net.graph['output'] = output

    return input, output


def stochastic_backprop(net, configs, ideal_output):
    # returns a float for error
    verbose = False

    activation_fn = configs['activation_function']
    learning_rate = float(configs['learning_rate'])
    MSE  = 0

    sorted_output_nodes = sorted(net.graph['output_nodes']) #fn doesn't matter as long as its consistent
    i = 0
    num_active_outputs = len(sorted_output_nodes)
    for output_node in sorted_output_nodes:

        if (net.node[output_node]['state'] is not None):
            # input hasn't reached all outputs yet, although outputs may now be emitting earlier (due to bias)

            output = net.node[output_node]['state']
            err = math.pow(ideal_output[i]-output,2)
            #print("\nOutput Node = " + str(output) + ", resulting in err = " + str(err))
            MSE += err
            if verbose: print('\nbackprop(): output of node = ' + str(output) + ", with err " + str(err))

            if (activation_fn == 'sigmoid'): activation_deriv = output*(1-output)
            elif (activation_fn == 'tanh'): activation_deriv = 1-math.pow(output,2)
            elif (activation_fn == 'linear'): activation_deriv = 1
            else: assert(None)

            err_deriv = (output-ideal_output[i])
            delta = err_deriv*activation_deriv

            for in_edge in net.in_edges(output_node):
                if net.node[in_edge[0]]['state']:
                    weight_contribution = net.node[in_edge[0]]['state'] #'weight contribution' is a misnomer...

                    if not util.boool(configs['out_edges_from_outputs']): assert(net.node[in_edge[0]] is not net.node[output_node])

                    partial_err = delta * weight_contribution
                    if verbose: print("delta = " + str(delta) + ", weight_contrib = " + str(weight_contribution) + ", curr_weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))
                    net[in_edge[0]][in_edge[1]]['weight'] -= partial_err*learning_rate
                    if verbose: print("now weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))

            # could add diff learning rate for the bias (typically lower)
            if verbose: print("old bias = " + str(net.node[output_node]['neuron_bias']) + ", its err contrib is delta = " + str(delta))
            net.node[output_node]['neuron_bias'] -= delta*learning_rate
            if verbose: print("new bias = " + str(net.node[output_node]['neuron_bias']))

        else: num_active_outputs -= 1

    if num_active_outputs == 0: return None

    if (num_active_outputs >0):
        MSE /= 2*num_active_outputs
        if verbose: print("\nReturning MSE of " + str(MSE) + " with " + str(num_active_outputs) + " active outputs.\n")
    return MSE


def step_fwd(net, configs):

    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']
    for n in net.nodes():
        if (net.node[n]['layer'] != 'input'):
            net.node[n]['state'] = activation(net, n, configs)

def save_states(net, configs):
    assert(configs['feedforward'])

    for n in net.nodes():
        net.node[n]['prev_iteration_state'] = net.node[n]['state']