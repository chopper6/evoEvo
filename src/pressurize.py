import instances, node_fitness, fitness, util, reservoir

def pressurize(configs, net, advice):
    # configs:
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])
    scale_node_fitness = util.boool(configs['scale_node_fitness'])
    directed = util.boool(configs['directed'])
    interval = configs['interval']

    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)


    if directed:
        assert (interval == 'continuous')

        err = 0 #err for base (1*) problem
        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            # note that node states not reset
            instance_err = reservoir.step(net, configs)
            if instance_err != None:
                err += instance_err
            fitness.calc_node_fitness(net, configs)

        net.graph['error'] = err / len(num_samples_relative)
        fitness.node_normz(net, num_samples_relative, configs)
        fitness_score = fitness.node_product(net, scale_node_fitness)

    else:

        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            instances.reset_states(net, configs)
            instances.experience(net, configs)
            fitness.calc_node_fitness(net, configs)

        fitness.node_normz(net, num_samples_relative, configs)
        fitness_score = fitness.node_product(net, scale_node_fitness)


    net.graph['fitness'] = fitness_score

