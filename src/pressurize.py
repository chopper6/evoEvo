import instances, node_fitness, fitness, util, probabilistic

def pressurize(configs, Net, advice, BD_table):
    # configs:
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])
    fitness_metric = str(configs['fitness_metric'])
    instance_states = str(configs['instance_states'])
    biased = util.boool(configs['biased'])
    scale_node_fitness = util.boool(configs['scale_node_fitness'])
    directed = util.boool(configs['directed'])

    net = Net.net #not great syntax, but Net is an individual in a population, whereas net is it's graph representation

    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)

    if (instance_states == 'probabilistic'): #NOTE: does not work well, but keeping for future tinkering
        assert(not biased or not configs['bias_on']=='nodes')
        fitness_score = probabilistic.calc_fitness(net, BD_table, configs)

    elif (instance_states == 'experience'):
        fitness.reset_fitness(net)
        for i in range(num_samples_relative):
            fitness.reset_node_spins(net)
            instances.experience(net, configs)
            fitness.calc_node_fitness(net, fitness_metric, directed)

        fitness.node_normz(net, num_samples_relative)
        fitness_score = fitness.node_product(net, scale_node_fitness)

    else:
        print("ERROR in pressurize: Unknown instance_source " + str(instance_states))
        return

    Net.fitness = fitness_score

