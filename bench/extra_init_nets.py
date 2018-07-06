
# OBSOLETE, poss use for init edge weights
def sign_edges(population):
    for p in range(len(population)):
        edge_list = population[p].net.edges()
        for edge in edge_list:
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1
            population[p].net[edge[0]][edge[1]]['sign'] = sign


def sign_edges_single(net):
    edge_list = net.edges()
    for edge in edge_list:
        sign = rd.randint(0, 1)
        if (sign == 0):     sign = -1
        net[edge[0]][edge[1]]['sign'] = sign


def double_edges(population):
    for p in range(len(population)):
        net = population[p].net
        edges = net.edges()
        for edge in edges:
            net.add_edge(edge[1], edge[0])  # add reverse edge



def other_saved_init_nets(init_type, pop_size, start_size):

    population = None

    ####################### OTHER NET TYPES, POSSIBLY OUTDATED ########################################
    if (init_type == 'shell'):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)]  # change to generate, based on start_size

    elif (init_type == 'erdos-renyi'):
        num_cc = 2
        num_tries = 0
        while(num_cc != 1):
            num_tries += 1
            init_net = (nx.erdos_renyi_graph(start_size,.035, directed=True, seed=None))
            num_added = 0
            for node in init_net.nodes():
                if (init_net.degree(node) == 0):
                    pre_edges = len(init_net.edges())
                    num_added += 1
                    sign = rd.randint(0, 1)
                    if (sign == 0):     sign = -1
                    node2 = node
                    while (node2 == node):
                        node2 = rd.sample(init_net.nodes(), 1)
                        node2 = node2[0]
                    if (rd.random() < .5): init_net.add_edge(node, node2, sign=sign)
                    else: init_net.add_edge(node2, node, sign=sign)
                    assert (len(init_net.edges()) > pre_edges)
                else:
                    if (init_net.in_edges(node) + init_net.out_edges(node) == 0): print("ERROR in net_generator(): hit a 0 deg node that is unrecognized.")

            net_undir = init_net.to_undirected()
            num_cc = nx.number_connected_components(net_undir)

        print("Number of added edges to avoid 0 degree = " + str(num_added) + ", num attempts to create suitable net = " + str(num_cc) + ".\n")
        population = [Net(init_net.copy(), i) for i in range(pop_size)]

    elif (init_type == 'empty'):
        population = [Net(nx.empty_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'complete'):
        #crazy high run time due to about n^n edges
        population = [Net(nx.complete_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'cycle'):
        population = [Net(nx.cycle_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 'star'):
        population = [Net(nx.star_graph(start_size-1), i) for i in range(pop_size)]
        custom_to_directed(population)

    elif (init_type == 'scale-free'):  # curr does not work, since can't go to undirected for output
        population = [Net(nx.scale_free_graph(start_size, beta=.7, gamma=.15, alpha=.15),i) for i in range(pop_size)]
    elif (init_type == 'barabasi-albert'):
        population = [Net(nx.barabasi_albert_graph(start_size, 2),i) for i in range(pop_size)]
        custom_to_directed(population)

    return population
