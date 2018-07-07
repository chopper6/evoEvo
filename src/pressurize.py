import instances, node_fitness, fitness, util, reservoir

def pressurize(configs, net, advice):
    # configs:
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])
    scale_node_fitness = util.boool(configs['scale_node_fitness'])
    directed = util.boool(configs['directed'])

    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)


    if directed:

        outputs = []
        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            # note that node states are not reset
            output = reservoir.step(net, configs)
            if output: outputs.append(output)
            fitness.calc_node_fitness(net, configs)

        # note this means that lvl 1 learning occurs at same rate
        # instead it should likely occur much faster
        net.graph['error'] = reservoir.linear_reg(net, outputs, configs)
        reservoir.lvl_1_learning(net, configs)  # TODO: add this fn() and see if err decreases

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

