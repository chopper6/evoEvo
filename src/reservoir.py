import math, networkx as nx, numpy as np, random as rd
import util, base_problem


def step(net, configs,  problem_instance = None):

    if problem_instance is None: input, output = base_problem.generate_instance(net, configs)
    else: input, output = problem_instance
    apply_input(net, input)
    one_step_fwd(net, configs)
    activate_err_nodes(net, output, configs)
    MSE = stochastic_backprop (net, output, configs)
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE


def feedfwd_step(net, configs):
    # possibly make this the more general model?

    input, output = base_problem.generate_instance(net, configs)
    apply_input(net, input)
    diameter = nx.diameter(net.to_undirected())
    for i in range(diameter): #all nodes should have had a chance to effect one another (except for directed aspect...)
        one_step_fwd(net, configs)
    activate_err_nodes(net, output, configs) #shouldn't really effect a feedfwd net
    MSE = stochastic_backprop (net, output, configs) #i.e. only care about last iteration
    lvl_1_reservoir_learning(net, configs)  # TODO: add this fn() and see if err decreases

    return MSE



def activation(net, node, configs):
    # curr linear activation with static bias (which is ~ thresh)
    # could add a few diff activation fns()
    # tech should exclude input_nodes, but shouldn't matter

    assert(net.node[node]['layer'] != 'input' and  net.node[node]['layer'] !='error') #inputs shouldn't be activated and errors have special activations
    activation_fn = configs['activation_function']

    # curr 2nd gen neurons

    sum = 0
    num_active = 0
    for edge in net.in_edges(node):
        #use previous state, since state is reserved for the new iteration (see one_step_fwd())
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



def initialize_input(net, configs):
    # supposed to be only at gen 0 if fully online learning
    # may later add diff initializations
    assert(not util.boool(configs['feedforward']))
    num_inputs = len(net.graph['input_nodes'])
    activn_fn = configs['activation_function']

    assert(num_inputs > 0)
    inputs = []

    if activn_fn == 'sigmoid':
        for i in range(num_inputs):
            inputs.append(rd.choice[0, 1])
            #inputs.append(rd.uniform(0,1))


    elif activn_fn == 'tanh':
        for i in range(num_inputs):
            inputs.append(rd.choice[-1,1]) #makes problem harder
            #inputs.append(rd.uniform(-1,1))

    else: assert(False)

    apply_input(net, inputs)






def lvl_1_reservoir_learning(net, configs):
    # alters weights in reservoir (as opposed to output layer)

    # TODO: add this
    return

    #learning = configs['lvl_1_learning']
    # can be greedy, naive_EA, or none



def stochastic_backprop(net, ideal_output, configs):
    # returns a float for error
    verbose = util.boool(configs['verbose_backprop'])

    activation_fn = configs['activation_function']
    learning_rate = float(configs['learning_rate'])
    bias_learning_rate = float(configs['bias_learning_rate'])
    regularization = util.boool(configs['regularization'])
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

            if verbose: print("\nerr = " + str(err_deriv) + ", output = " + str(output) + " vs ideal = " + str(ideal_output[i]))
            for in_edge in net.in_edges(output_node):
                if net.node[in_edge[0]]['state']:
                    weight_contribution = net.node[in_edge[0]]['state'] #'weight contribution' is a misnomer...

                    partial_err = delta * weight_contribution
                    if verbose: print("delta = " + str(delta) + ", weight_contrib = " + str(weight_contribution) + ", curr_weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))
                    w_change = partial_err*learning_rate
                    if regularization and abs(net[in_edge[0]][in_edge[1]]['weight']) > .01: w_change /= abs(net[in_edge[0]][in_edge[1]]['weight'])
                    #TODO: add more intelligent regularization, add to bias too, and test it

                    net[in_edge[0]][in_edge[1]]['prev_weight'] = net[in_edge[0]][in_edge[1]]['weight']
                    net[in_edge[0]][in_edge[1]]['weight'] -= w_change
                    if verbose: print("now weight = " + str(net[in_edge[0]][in_edge[1]]['weight']))

            # could add diff learning rate for the bias (typically lower)
            if verbose: print("old bias = " + str(net.node[output_node]['neuron_bias']) + ", its err contrib is delta = " + str(delta))
            net.node[output_node]['prev_neuron_bias'] = net.node[output_node]['neuron_bias']
            net.node[output_node]['neuron_bias'] -= delta*bias_learning_rate
            if verbose: print("new bias = " + str(net.node[output_node]['neuron_bias']))

        else: num_active_outputs -= 1

    if num_active_outputs == 0: return None

    if (num_active_outputs >0):
        MSE /= 2*num_active_outputs
        if verbose: print("\nReturning MSE of " + str(MSE) + " with " + str(num_active_outputs) + " active outputs.\n\n")
    return MSE


def one_step_fwd(net, configs):
    for n in net.nodes():
        net.node[n]['prev_state'] = net.node[n]['state']

    for n in net.nodes():
        if (net.node[n]['layer'] != 'input' and net.node[n]['layer'] !='error'):
            net.node[n]['state'] = activation(net, n, configs)

        if util.boool(configs['debug']):
            if net.node[n]['layer'] == 'error':
                assert(net.node[n]['neuron_bias']==0) #backprop should never touch it, but later additions might


def save_prev_iteration_states(net, configs):
    assert(configs['feedforward'])

    for n in net.nodes():
        net.node[n]['prev_iteration_state'] = net.node[n]['state']


def activate_err_nodes(net, ideal_output, configs):

    sorted_output_nodes = sorted(net.graph['output_nodes'])
    i=0
    for output_node in sorted_output_nodes:

        if (net.node[output_node]['state'] is not None):
            # input hasn't reached all outputs yet, although outputs may now be emitting earlier (due to bias)

            err_node = find_error_buddy(net,output_node)
            output = net.node[output_node]['state']
            err = math.pow(ideal_output[i] - output, 2) #TODO: use partial error instead?
            net.node[err_node]['state'] = err
            if net.node[err_node]['ideal_output'] is not None:
                net.node[err_node]['prev_ideal_output'] = net.node[err_node]['ideal_output']
            net.node[err_node]['ideal_output'] = ideal_output[i] #TODO: clean this sloppy shit


        i+=1

def find_error_buddy(net,output_node):
    for out_edge in net.out_edges(output_node):
        if net.node[out_edge[1]]['layer'] == 'error': return out_edge[1]

    print("ERROR in reservoir.find_error_buddy(): output has no associated error nodes.")
    assert(False)
