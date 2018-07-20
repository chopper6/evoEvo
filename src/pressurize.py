import instances, node_fitness_discrete, node_fitness_continuous, fitness, util, reservoir, output

def pressurize(configs, net, gen, problem_instances = None):
    # configs:
    scale_node_fitness = util.boool(configs['scale_node_fitness'])
    directed = util.boool(configs['directed'])
    feedfwd = util.boool(configs['feedforward'])

    num_samples_relative = num_samples(net, configs)
    if problem_instances:
        assert(len(problem_instances) == num_samples_relative)
        assert(not feedfwd)
    else: problem_instances = [None for i in range(num_samples_relative)]


    if directed:

        total_err, num_outputs = 0, 0
        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            # note that node states are not reset
            if not feedfwd: err = reservoir.step(net, configs, problem_instance = problem_instances[i])
            else: err = reservoir.feedfwd_step(net, configs)
            if (err is not None): #TODO: error nodes may not yet be active
                total_err += err
                num_outputs += 1
            fitness.calc_node_fitness(net, configs)
            output.write_base_err(configs, gen, i, err)
            if feedfwd: reservoir.save_prev_iteration_states(net, configs) #TODO: might not make sense if problem_instances given

        if num_outputs==0:  net.graph['error'] = None
        else:               net.graph['error'] = total_err / num_outputs

        fitness.node_normz(net, num_samples_relative, configs)
        #TODO: unbalanced issue: later nodes may have more 'None' instances, at least for not feedfwd, ensures that input has reached output (may penalize some hidden folks)

        fitness_score = fitness.node_product(net, scale_node_fitness, configs)

    else:

        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            instances.reset_states(net, configs)
            instances.experience(net, configs)
            fitness.calc_node_fitness(net, configs)

        fitness.node_normz(net, num_samples_relative, configs)
        fitness_score = fitness.node_product(net, scale_node_fitness, configs)


    net.graph['fitness'] = fitness_score



def num_samples(net, configs):
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])

    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)

    return num_samples_relative

