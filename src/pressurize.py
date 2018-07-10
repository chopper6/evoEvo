import instances, node_fitness, fitness, util, reservoir, output
import networkx as nx

def pressurize(configs, net, gen):
    # configs:
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])
    scale_node_fitness = util.boool(configs['scale_node_fitness'])
    directed = util.boool(configs['directed'])
    feedfwd = util.boool(configs['feedforward'])

    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)


    if directed:

        total_err, num_outputs = 0, 0
        fitness.reset_nodes(net, configs)
        for i in range(num_samples_relative):
            # note that node states are not reset
            if not feedfwd: err = reservoir.step(net, configs)
            else:
                diameter = nx.diameter(net)
                err = reservoir.feedfwd_step(net, configs, diameter)
            if (err != None):
                total_err += err
                num_outputs += 1
            fitness.calc_node_fitness(net, configs)
            output.write_base_err(configs, gen, i, err)

        if num_outputs==0:  net.graph['error'] = None
        else:               net.graph['error'] = total_err / num_outputs

        fitness.node_normz(net, num_samples_relative, configs) #TODO: may be later nodes with more 'None' instances
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

