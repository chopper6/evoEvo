import random as rd
import pressurize, reservoir, build_nets, util, mutate

def generate_net_instances(teacher_net, configs):
    # reservoir steps fwd to generate instances
    # does NOT handle mutation of net

    base_problem = configs['base_problem']
    feedfwd = util.boool(configs['feedforward'])
    assert(base_problem == 'teacher' and not feedfwd) #could add feedfwd version later

    num_samples_relative = pressurize.num_samples(teacher_net, configs) #assumes that all nets are same size
    instances = []

    for i in range(num_samples_relative):
        inputs, outputs = [], []
        finished_reservoir_outputs = None
        while not finished_reservoir_outputs:
            reservoir.step_fwd(teacher_net, configs) #occurs at least once
            finished_reservoir_outputs = True
            for output in teacher_net.graph['output_nodes']:
                if teacher_net.node[output]['state'] is None:
                    finished_reservoir_outputs = False

        for input in teacher_net.graph['input_nodes']:
            inputs.append(teacher_net.node[input]['state'])
        for output in teacher_net.graph['output_nodes']:
            outputs.append(teacher_net.node[output]['state'])
        instances.append([inputs, outputs])

    return instances


def step_teacher_net(teacher_net, gen, configs):

    assert(not util.boool(configs['biased'])) #else need to pass to mutate

    #returns problem instances
    reservoir.initialize_input(teacher_net, configs) #for fully online learning this may not be nec
    if gen !=0: mutate.mutate(configs, teacher_net) #as in minion
    instances = generate_net_instances(teacher_net, configs)

    return instances


def generate_instance(net, configs):
    # returns input and output, as well as saving them (and their previous iteration) to the net
    # TODO: add a biased pr one

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