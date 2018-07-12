import random as rd, networkx as nx
import bias, util, init_nets

def mutate(configs, net, biases = None):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    # GROW (ADD NODE)
    num_grow = num_mutations(grow_freq)
    if (num_grow > 0): add_nodes(net, num_grow, configs, biases=biases)

    # SHRINK (REMOVE NODE)
    # WARNING: poss outdated
    num_shrink = num_mutations(shrink_freq)
    if (num_shrink > 0): shrink(net, num_shrink, configs)

    # REWIRE EDGE
    num_rewire = num_mutations(rewire_freq)
    rewire(net, num_rewire, configs)

    # CHANGE EDGE SIGN
    # WARNING: poss outdated
    num_sign = num_mutations(sign_freq)
    if (num_sign > 0): change_edge_sign(net, num_sign)

    ensure_single_cc(net, configs)




################################ MUTATIONS ################################
def add_nodes(net, num_add, configs, biases=None, layer = None):

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    directed = util.boool(configs['directed'])

    if biases: assert(biased)
    # note that the converse may not be true: net_generator will mutate first and add biases later

    # ADD NODE
    for i in range(num_add):
        print("\nadding node #" + str(i))
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            new_node = rd.randint(0, len(net.nodes()) * 10000)  # hope to hit number that doesn't already exist
            if new_node not in net.nodes(): #could slow things down...
                net.add_node(new_node)
                post_size = len(net.nodes())
                assert(pre_size < post_size)
            print("new node = " + str(new_node))
        if biases and bias_on == 'nodes': bias.assign_a_node_bias(net, new_node, configs['bias_distribution'], given_bias=biases[i])

        if directed:
            if not layer: net.node[new_node]['layer'] = 'hidden'
            else:
                net.node[new_node]['layer'] = layer
                if layer=='input': net.graph['input_nodes'].append(new_node)
                elif layer=='output': net.graph['output_nodes'].append(new_node)
            net.node[new_node]['state'] = None
            net.node[new_node]['neuron_bias'] = init_nets.assign_edge_weight(configs)

        # ADD EDGE TO NEW NODE TO KEEP CONNECTED
        if biases and bias_on=='edges': add_this_edge(net, configs, node1=new_node, given_bias=biases[i])
        else: add_this_edge(net, configs, node1=new_node)

        if util.boool(configs['single_cc']): ensure_single_cc(net, configs)


    # MAINTAIN NODE_EDGE RATIO
    num_edge_add = int(num_add * float(configs['edge_to_node_ratio'])) - num_add
    if biases and bias_on == 'edges':
        assert(len(biases) == num_edge_add + num_add)
        add_edges(net, num_edge_add, configs, biases=biases[num_add:])
    else:  add_edges(net, num_edge_add, configs)

    if util.boool(configs['single_cc']):
        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)
        assert(num_cc == 1)

def shrink(net, num_shrink, configs):
    #WARNING: outdated, ex directed
    assert(False)

    pre_size = len(net.nodes())
    for i in range(num_shrink):

        #REMOVE NODE
        node = rd.sample(net.nodes(), 1)
        node = node[0]

        num_edges_lost = len(net.in_edges(node)+net.out_edges(node)) #ASSUmeS directional reduction
        change_in_edges = 2-num_edges_lost

        net.remove_node(node)
        post_size = len(net.nodes())
        if (pre_size == post_size): print("MUTATE SHRINK() ERR: node not removed.")

        # MAINTAIN NODE:EDGE RATIO
        if (change_in_edges > 0): rm_edges(net,change_in_edges, configs)
        else: add_edges(net, -1*change_in_edges, configs)


def rewire(net, num_rewire, configs):
    single_cc = util.boool(configs['single_cc'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])

    for i in range(num_rewire):

        assert(edge_node_ratio!=1 or not single_cc)
        # this is an unlikely scenario, but bias tracking requires rm, then add
        # which triggers multiple connected components if edge_node_ratio = 1

        orig_biases = rm_edges(net,1,configs)
        add_this_edge(net, configs, given_bias=orig_biases[0])



def change_edge_sign(net, num_sign):
    # WARNING: poss outdated

    for i in range(num_sign):
        pre_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
            post_edges = len(net.edges())
            if (post_edges != pre_edges): print("ERROR IN SIGN CHANGE: num edges not kept constant.")



############################### EDGE FUNCTIONS ################################
def add_edges(net, num_add, configs, biases=None):

    #if (num_add == 0): print("WARNING in mutate(): 0 nodes added in add_nodes\n")

    if (biases):
        assert (len(biases)==num_add)
        assert (util.boool(configs['biased'])) # note that the converse may not be true: net_generator will mutate first and add biases later

    for j in range(num_add):
        if (biases): add_this_edge(net,configs, given_bias=biases[j])
        else: add_this_edge(net, configs)



def add_this_edge(net, configs, node1=None, node2=None, sign=None, given_bias=None):

    directed = util.boool(configs['directed'])
    self_loops = util.boool(configs['self_loops'])
    single_cc = util.boool(configs['single_cc'])
    bias_on = configs['bias_on']

    node1_set, node2_set = node1, node2 #to save their states

    if not sign:
        sign = rd.randint(0, 1)
        if (sign == 0): sign = -1

    pre_size = post_size = len(net.edges())
    i=0
    while (pre_size == post_size):  # ensure that net adds

        if node1_set is None:
            node = rd.sample(net.nodes(), 1)
            node1 = node[0]

        if node2_set is None:
            if self_loops:
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            else: #make sure that edge is not to self
                node2 = node1
                while (node2 == node1):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]

        #chance to swap nodes 1 & 2
        if (rd.random()<.5):
            node3=node2
            node2=node1
            node1=node3

        constraints_check = check_constraints(net, node1, node2, configs)

        if constraints_check:
            net.add_edge(node1, node2, sign=sign)
            if directed: net[node1][node2]['weight'] = init_nets.assign_edge_weight(configs)

        post_size = len(net.edges())
        if constraints_check: assert(post_size != pre_size)

        i+=1
        if (i == 100000):
            util.cluster_print(configs['output_directory'], "\n\n\nWARNING mutate.add_this_edge() is looping a lot.\nNode1 = " + str(node1_set) + ", Node2 = " + str(node2_set) +  "\n\n\n")
            assert(False)

    if (bias and bias_on == 'edges'): bias.assign_an_edge_bias(net, [node1,node2], configs['bias_distribution'], given_bias=given_bias)


def rm_edges(net, num_rm, configs):
    # constraints: doesn't leave 0 deg edges or mult connected components (if configs don't allow them)

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    orig_biases = []

    for j in range(num_rm):
        pre_size = post_size = len(net.edges())
        i=0
        while (pre_size == post_size):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0] #just cause sample returns [edge]

            if util.boool(configs['single_cc']):
                # don't allow edges w/ 1 deg (which would then be severed from graph
                while ((net.in_degree(edge[0]) + net.out_degree(edge[0]) == 1) or (net.in_degree(edge[1]) + net.out_degree(edge[1]) == 1)):
                    edge = rd.sample(net.edges(), 1)
                    edge = edge[0]

            sign_orig = net[edge[0]][edge[1]]['sign']
            if biased and bias_on == 'edges': bias_orig = net[edge[0]][edge[1]]['bias']
            else: bias_orig = None
            orig_biases.append(bias_orig)

            net.remove_edge(edge[0], edge[1])

            post_size = len(net.edges())
            i+=1

            if (i==10000): 
                util.cluster_print(configs['output_directory'], "WARNING mutate.rm_edges() is looping a lot.\n")
                assert(False)

        ensure_single_cc(net, configs, node1=edge[0], node2=edge[1], sign_orig=sign_orig, bias_orig=bias_orig)

    return orig_biases



################################ MISC HELPER FUNCTIONS ################################
def num_mutations(base_mutn_freq):

    if base_mutn_freq >= 1: mutn_freq = int(base_mutn_freq)
    else: mutn_freq = base_mutn_freq

    if (mutn_freq == 0): return 0
    elif (mutn_freq >= 1): return int(mutn_freq)
    elif (mutn_freq < 1):
        if (rd.random() < mutn_freq): return 1
        else: return 0
    else:
        print("ERROR in mutate.num_mutations(): mutation should be < 1 OR, if > 1, an INT")
        assert(False)


def ensure_single_cc(net, configs, node1=None, node2=None, sign_orig=None, bias_orig=None):
    #rewires [node1, node2] at the expense of a random, non deg1 edge

    # note that allowing multiple connected components may actually improve EA by increasing neutral mutation space

    single_cc = util.boool(configs['single_cc'])

    if single_cc:

        nodes_given = False
        if node1 is not None:
            assert(node2 is not None)
            nodes_given = True
        elif not node1: assert not (node2)

        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)

        if (num_cc != 1): #rm_edge() will recursively check #COULD CAUSE AN INFINITE LOOP
            components = list(nx.connected_components(net_undir))
            constraints_check = False

            i = 0
            while not constraints_check:
                if node1 is None:
                    c1 = components[0]
                    node1 = rd.sample(c1, 1)
                    node1 = node1[0]

                if node2 is None:
                    c2 = components[1]
                    node2 = rd.sample(c2, 1)
                    node2 = node2[0]

                if not sign_orig:
                    sign_orig = rd.randint(0, 1)
                    if (sign_orig == 0): sign_orig = -1

                # chance to swap nodes 1 & 2
                if (rd.random() < .5):
                    node3 = node2
                    node2 = node1
                    node1 = node3

                constraints_check = check_constraints(net, node1, node2, configs)
                if constraints_check == False:
                    i += 1
                    assert(nodes_given == False) #since they'll never change
                    if (i >= 100000):
                        print("ERROR in mutate.ensure_single_cc():\n layers of component 1 = ")
                        for n in c1:
                            print(net.node[n]['layer'])
                        print("layers of components 2 = ")
                        for n in c2:
                            print(net.node[n]['layer'])

                        assert(False)



            add_this_edge(net, configs, node1=node1, node2=node2, sign=sign_orig, given_bias=bias_orig)
            rm_edges(net, 1, configs) #calls ensure_single_cc() at end


        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)
        assert (num_cc == 1)



def check_constraints(net, node1, node2, configs):
    # returns true if constraints held, false otherwise
    directed = util.boool(configs['directed'])
    self_loops = util.boool(configs['self_loops'])
    single_cc = util.boool(configs['single_cc'])

    if directed:
        if net.node[node2]['layer'] == 'input': return False
        if not util.boool(configs['out_edges_from_outputs']):
            if net.node[node1]['layer'] == 'output': return False

        if net.has_edge(node1, node2): return False

    else:
        if net.has_edge(node1, node2) or net.has_edge(node2, node1): return False

    if not self_loops:
        if node1==node2: return False

    return True
