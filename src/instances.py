import util
import random as rd


def experience(net, configs):

    directed = util.boool(configs['directed'])
    assert (not directed) #TODO: implement directed

    pressure_on = configs['pressure_on']
    pressure = float(float(configs['pressure'])/float(100))

    interval = configs['interval']
    assert(interval == 'discrete' or interval == 'continuous')


    if (interval == 'continuous'):
        env_distrib = configs['env_distribution']
        assert (env_distrib == 'uniform' or env_distrib == 'normal')
        assert(pressure_on == 'edges')
        biased = util.boool(configs['biased'])
        assert(not biased)

        pressure_relative = int(len(net.edges()) * pressure)
        edges = net.edges()
        rd.shuffle(edges)

        for edge in edges[:pressure_relative]:
            env_state = 0
            #TODO: edges that aren't pressurized remain as previous state? or set to none?
            if env_distrib == 'uniform':
                env_state = rd.uniform(-1,1)
            elif env_distrib == 'normal':
                env_state = rd.gauss(0,1)
            net[edge[0]][edge[1]]['state'] = env_state
            if (rd.random()< .01): print("[instances.py] ex edge state = " + str(env_state))


    elif (interval == 'discrete'):
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




def reset_states(net, configs):
    interval = configs['interval']
    pressure_on = configs['pressure_on']
    assert(interval == 'discrete' or interval == 'continuous')

    if interval == 'discrete':

        for n in net.nodes():
            net.node[n]['up'] = 0
            net.node[n]['down'] = 0

    elif interval == 'continuous':

        assert(pressure_on == 'edges')
        for edge in net.edges():
            net[edge[0]][edge[1]]['state'] = None