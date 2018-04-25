import util
import random as rd


def experience(net, configs):

    directed = util.boool(configs['directed'])
    assert (not directed) #TODO: implement directed

    pressure_on = configs['pressure_on']
    pressure = float(float(configs['pressure'])/float(100))

    if pressure_on == 'edges':

        pressure_relative = int(len(net.edges()) * pressure)
        edges = net.edges()
        rd.shuffle(edges)

        for edge in edges[:pressure_relative]:
            advice = util.single_advice(net, edge, configs)
            if advice == 1:
                net.node[edge[0]]['up'] += 1
                net.node[edge[1]]['up'] += 1
            else: #advice == -1
                net.node[edge[0]]['down'] += 1
                net.node[edge[1]]['down'] += 1

    else:
        assert(pressure_on == 'nodes')

        pressure_relative = int(len(net.nodes()) * pressure)
        nodes = net.nodes()
        rd.shuffle(nodes)
        pressured_nodes = nodes[:pressure_relative]

        for edge in net.edges():
            if edge[0] in pressured_nodes and edge[1] in pressured_nodes:
                advice = util.single_advice(net, edge, configs)
                if advice == 1:
                    net.node[edge[0]]['up'] += 1
                    net.node[edge[1]]['up'] += 1
                else: #advice == -1
                    net.node[edge[0]]['down'] += 1
                    net.node[edge[1]]['down'] += 1


