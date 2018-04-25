import random as rd

# THIS LIKELY NEEDS TO BE DEBUGGED
# GIST OF EXPERIMENT: TAKE A REAL NET, SCRAMBLE A NUMBER OF EDGES, THEN START SIM

def scramble_edges(net, percent):
    #changes connectivity while maintaining same number of edges
    #conserves sign

    edge_list = net.edges()
    num_scramble = round(percent*len(edge_list))
    #print("perturb(): scrambling " + str(num_scramble) + " edges.")

    signs = [] #could also include sign data in init edge_list but oh well
    
    for edge in edge_list[:num_scramble]:
        signs.append(net[edge[0]][edge[1]]['sign'])
        net.remove_edge(edge[0], edge[1])

    i=0
    for edge in edge_list[:num_scramble]:

        pre_size = post_size = len(net.edges())
        while (pre_size == post_size):  # ensure that net adds
            node = node2 = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            orig_sign = signs[i] 
            net.add_edge(node, node2, sign=orig_sign)
            post_size = len(net.edges())
        i+=1
    


def num_edges(net, multiplier):
    orig_num_edges = len(net.edges())

    if (multiplier > 0): #ADD
        add_num = orig_num_edges*multiplier
        print("perturb(): adding " + str(add_num) + " edges.")

        for i in range(add_num):
            pre_size = post_size = len(net.edges())
            while (pre_size == post_size):  # ensure that net adds
                node = node2 = rd.sample(net.nodes(), 1)
                node = node[0]
                node2 = node
                while (node2 == node):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = rd.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_size = len(net.edges())

    else: #REMOVE
        rm_num = -1 * orig_num_edges * multiplier

        print("perturb(): removing " + str(rm_num) + " edges.")

        for i in range(rm_num):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            net.remove_edge(edge[0], edge[1])



def num_nodes(net, multiplier):
    orig_num_nodes = len(net.nodes())

    if (multiplier > 0): #ADD
        add_num = orig_num_nodes*multiplier
        print("perturb(): adding " + str(add_num) + " nodes.")

        for i in range(add_num):
            pre_size = post_size = len(net.nodes())
            while(pre_size == post_size):
                node_num = rd.randint(0,len(net.nodes())*100000) #hope to hit number that doesn't already exist
                net.add_node(node_num)
                post_size = len(net.nodes())


    else: #REMOVE
        orig_num_edges = len(net.edges())
        rm_num = -1 * orig_num_edges * multiplier
        print("perturb(): removing " + str(rm_num) + " nodes.")

        for i in range(rm_num):
            node = rd.sample(net.nodes(), 1)
            node = node[0]
            net.remove_node(node)
