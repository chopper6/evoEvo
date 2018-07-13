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
    if util.boool(configs['directed']): check_layers(net, configs)



################################ MUTATIONS ################################
def add_nodes(net, num_add, configs, biases=None, layer = None):

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    directed = util.boool(configs['directed'])

    node1_layer, node2_layer = None, None
    if layer == 'input':     node1_layer = 'input'
    elif layer == 'output':  node2_layer = 'output'

    if directed: assert(not biased) #not ready for that shit yet

    if biases: assert(biased)
    # note that the converse may not be true: net_generator will mutate first and add biases later

    # ADD NODE
    for i in range(num_add):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            new_node = rd.randint(0, len(net.nodes()) * 10000)  # hope to hit number that doesn't already exist
            if new_node not in net.nodes(): #could slow things down...
                net.add_node(new_node)
                post_size = len(net.nodes())
                assert(pre_size < post_size)
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
        else: add_this_edge(net, configs, node1=new_node, node1_layer = node1_layer, node2_layer = node2_layer)
        assert(net.in_edges(new_node) or net.out_edges(new_node))

        if util.boool(configs['single_cc']): ensure_single_cc(net, configs)


    # MAINTAIN NODE_EDGE RATIO
    if layer == 'input': num_edge_add = int(num_add * float(configs['from_inputs_edge_ratio'])) - num_add
    elif layer == 'output': num_edge_add = int(num_add * float(configs['to_outputs_edge_ratio'])) - num_add
    else: num_edge_add = int(num_add * float(configs['edge_to_node_ratio'])) - num_add
    if biases and bias_on == 'edges':
        assert(len(biases) == num_edge_add + num_add)
        add_edges(net, num_edge_add, configs, biases=biases[num_add:])
    else:  add_edges(net, num_edge_add, configs, node1_layer = node1_layer, node2_layer = node2_layer)

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

        orig_bias = rm_an_edge(net,configs)
        add_this_edge(net, configs, given_bias=orig_bias)



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
def add_edges(net, num_add, configs, biases=None, node1_layer=None, node2_layer=None):

    #if (num_add == 0): print("WARNING in mutate(): 0 nodes added in add_nodes\n")

    if (biases):
        assert (len(biases)==num_add)
        assert (util.boool(configs['biased'])) # note that the converse may not be true: net_generator will mutate first and add biases later
        assert (not util.boool(configs['directed']))
    for j in range(num_add):
        if (biases): add_this_edge(net,configs, given_bias=biases[j])
        else: add_this_edge(net, configs,  node1_layer=node1_layer, node2_layer=node2_layer)


def add_this_edge(net, configs, node1=None, node2=None, sign=None, given_bias=None, node1_layer=None, node2_layer=None):
    # if node1['layer'] = 'input' or node2['layer'] = 'output', rewires an appropriate layer


    directed = util.boool(configs['directed'])
    bias_on = configs['bias_on']

    node1_set, node2_set = node1, node2 #to save their states

    if not sign:
        sign = rd.randint(0, 1)
        if (sign == 0): sign = -1

    if node1_layer=='input': assert(node2_layer != 'input')

    pre_size = post_size = len(net.edges())
    i=0
    while (pre_size == post_size):  # ensure that net adds

        if node1_set is None: node1 = sample_node(net, node1_layer)
        else: node1 = node1_set

        if node2_set is None: node2 = sample_node(net, node2_layer)
        else: node2 = node2_set

        #chance to swap nodes 1 & 2
        if node1_set is None or node2_set is None and node1_layer is None and node2_layer is None:
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
        if (i == 1000000):
            util.cluster_print(configs['output_directory'], "\n\n\nERROR mutate.add_this_edge() is looping a lot.\nNode1 = " + str(node1_set) + ", Node2 = " + str(node2_set) +  "\n\n\n")
            if node1_set is not None: print("node1 layer = " + str(net.node[node1_set]['layer']))
            if node2_set is not None: print("node2 layer = " + str(net.node[node2_set]['layer']))
            assert(False)

    if (bias and bias_on == 'edges'): bias.assign_an_edge_bias(net, [node1,node2], configs['bias_distribution'], given_bias=given_bias)

    if net.node[node1]['layer']=='input' and node1_layer != 'input':
        rm_an_edge(net,configs, layer='input') # need to rebalance input layer
        add_this_edge(net,configs) # need to compensate for rm'd edge
    if net.node[node2]['layer']=='output' and node2_layer != 'output':
        rm_an_edge(net,configs,layer='output')
        add_this_edge(net,configs)


def rm_an_edge(net, configs, layer=None):
    # constraints: doesn't leave 0 deg edges or mult connected components (if configs don't allow them)

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    orig_biases = []
    directed = util.boool(configs['directed'])

    bias_orig, node1_layer, node2_layer = None, None, None

    pre_size = post_size = len(net.edges())
    i = 0
    while (pre_size == post_size):
        edge = sample_edge(net, layer)

        if util.boool(configs['single_cc']):
            # don't allow edges w/ 1 deg (which would then be severed from graph
            while ((net.in_degree(edge[0]) + net.out_degree(edge[0]) == 1) or (net.in_degree(edge[1]) + net.out_degree(edge[1]) == 1)):
                edge = rd.sample(net.edges(), 1)
                edge = edge[0]

        sign_orig = net[edge[0]][edge[1]]['sign']
        if biased and bias_on == 'edges':
            bias_orig = net[edge[0]][edge[1]]['bias']
        else:
            bias_orig = None
        orig_biases.append(bias_orig)

        net.remove_edge(edge[0], edge[1])

        if directed:
            if net.nodes[edge[0]]['layer'] == 'input': node1_layer = 'input'
            if net.nodes[edge[1]]['layer'] == 'output': node2_layer = 'output'
            #output as source node is irrelevant (not separately tracked)

        post_size = len(net.edges())
        i += 1

        if (i == 10000):
            util.cluster_print(configs['output_directory'], "WARNING mutate.rm_an_edge() is looping a lot.\n")
            assert (False)

    ensure_single_cc(net, configs, node1=edge[0], node2=edge[1], sign_orig=sign_orig, bias_orig=bias_orig)

    if layer is None and (node1_layer is not None or node2_layer is not None):
        add_this_edge(net,configs, node1_layer=node1_layer, node2_layer=node2_layer)
        rm_an_edge(net, configs)

    return bias_orig


def rm_edges(net, num_rm, configs):
    # constraints: doesn't leave 0 deg edges or mult connected components (if configs don't allow them)

    orig_biases = []
    directed = util.boool(configs['directed'])
    assert(not directed) #would have to deal with layer shit

    for j in range(num_rm):
        orig_bias, node1_layer, node2_layer = rm_an_edge(net,configs)
        orig_biases.append(orig_bias)

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

    node1_set, node2_set = node1, node2

    if single_cc:

        if node1 is not None: assert(node2 is not None)
        elif not node1: assert not (node2)

        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)

        if (num_cc != 1): #rm_edge() will recursively check #COULD CAUSE AN INFINITE LOOP
            components = list(nx.connected_components(net_undir))
            constraints_check = False

            i = 0
            while not constraints_check:
                if node1_set is None:
                    c1 = components[0]
                    node1 = rd.sample(c1, 1)
                    node1 = node1[0]
                else: node1 = node1_set

                if node2_set is None:
                    c2 = components[1]
                    node2 = rd.sample(c2, 1)
                    node2 = node2[0]
                else: node2 = node2_set

                if not sign_orig:
                    sign_orig = rd.randint(0, 1)
                    if (sign_orig == 0): sign_orig = -1

                # chance to swap nodes 1 & 2
                # if they are pre-designated, don't assume switch is ok
                if node1_set is None or node2_set is None:
                    if (rd.random() < .5):
                        node3 = node2
                        node2 = node1
                        node1 = node3

                constraints_check = check_constraints(net, node1, node2, configs)
                if constraints_check == False:
                    i += 1
                    if (i >= 100000):
                        print("ERROR in mutate.ensure_single_cc():\n layers of component 1 = ")
                        assert(False)


            add_this_edge(net, configs, node1=node1, node2=node2, sign=sign_orig, given_bias=bias_orig)
            rm_an_edge(net, configs) #calls ensure_single_cc() at end


        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)
        assert (num_cc == 1)



def check_constraints(net, node1, node2, configs):
    # returns true if constraints held, false otherwise
    directed = util.boool(configs['directed'])
    self_loops = util.boool(configs['self_loops'])

    if directed:
        if net.node[node2]['layer'] == 'input': return False
        if not util.boool(configs['out_edges_from_outputs']):
            if net.node[node1]['layer'] == 'output': return False

        if net.node[node1]['layer'] == 'input' and net.node[2]['layer'] == 'output': return False
        #this one is not objectionable to the model, it's just a giant flagpole up the ass
        #would have to anticipate rewire scenarios where edge[input][output] is rm'd
        #then rebalancing is req'd (to maintain requested num of input and output edges)...ect, ect

        if net.has_edge(node1, node2): return False

    else:
        if net.has_edge(node1, node2) or net.has_edge(node2, node1): return False

    if not self_loops:
        if node1==node2: return False

    return True


def sample_node(net, layer):

    if layer is None:
        node = rd.sample(net.nodes(), 1)
    elif layer == 'input':
        node = rd.sample(net.graph['input_nodes'],1)
    elif layer == 'output':
        node = rd.sample(net.graph['output_nodes'],1)
    else: assert(False)

    node1 = node[0]
    return node1


def sample_edge(net, layer):

    if layer is None:
        edge = rd.sample(net.edges(), 1)
    elif layer == 'input':
        edge = rd.sample(net.out_edges(net.graph['input_nodes']))
    elif layer == 'output':
        edge = rd.sample(net.in_edges(net.graph['output_nodes']))
    else: assert(False)

    edge = edge[0]  # just cause sample returns [edge]
    return edge


def check_layers(net, configs):

    # check input e2n
    num_edges_from_inputs = len(net.out_edges(net.graph['input_nodes']))
    ideal_num_edges = int(len(net.graph['input_nodes']) * float(configs['from_inputs_edge_ratio']))

    if num_edges_from_inputs != ideal_num_edges:
        print("ERROR in mutate.check_layers(): actual num INPUT edges = " + str(num_edges_from_inputs) + ", but should be " + str(ideal_num_edges))
        assert(False)

    # check output e2n
    num_edges_to_outputs = len(net.in_edges(net.graph['output_nodes']))
    ideal_num_edges = int(len(net.graph['input_nodes']) * float(configs['to_outputs_edge_ratio']))

    if num_edges_to_outputs != ideal_num_edges:
        print("ERROR in mutate.check_layers(): actual num OUTPUT edges = " + str(num_edges_to_outputs) + ", but should be " + str(ideal_num_edges))
        assert (False)


    # check hidden e2n
    num_edges = len(net.edges()) - num_edges_to_outputs - num_edges_from_inputs
    reservoir_size = len(net.nodes()) - len(net.graph['output_nodes']) - len(net.graph['input_nodes'])
    ideal_num_edges = int(float(configs['edge_to_node_ratio']) * reservoir_size)

    if num_edges != ideal_num_edges:
        print("ERROR in mutate.check_layers(): actual num RESERVOIR edges = " + str(num_edges) + ", but should be " + str(ideal_num_edges))
        assert (False)
