import math

def calc_discrete_directed (net, node, fitness_metric):
    num0, num1 = 0, 0

    for e in net.in_edges(node):
        if net.node[e[0]]['state'] == 0: num0 += 1
        elif net.node[e[0]]['state'] == 1: num1 += 1

    if (num0 + num1 ==0): return 0

    elif (fitness_metric == 'info'):
        return 1-shannon_entropy(num0,num1)

    else: print("ERROR in node_fitness.calc_discrete_directed(): unknown fitness metric: " + str(fitness_metric))


def calc_discrete_undirected (fitness_metric, up, down):
    if (up + down ==0): return 0

    if (fitness_metric == 'info'):
        return 1-shannon_entropy(up,down)

    else: print("ERROR in node_fitness.calc_discrete_undirected(): unknown fitness metric: " + str(fitness_metric))



def calc_continuous (states, fitness_metric, distrib_lng=1):
    mean = sum(states)/len(states)
    var, entropish = 0, 0
    # may have to change distrib_lng if, for ex. states can be in [-1,1]

    for state in states:
        var += math.pow((mean-state),2)
        pr = 1-abs(mean-state)/ float(distrib_lng)
        assert(pr >= 0 and pr <= 1)
        if pr != 0:
            entropish -= math.log2(pr)

    if (len(states) > 1): var /= len(states) - 1
    if (len(states) > 0): entropish /= len(states)

    if var == 0:
        fitness = 1
        return fitness

    fitness = None

    if (fitness_metric == 'entropish'):
        return entropish

    elif (fitness_metric == 'variance'):
        fitness = var

    elif (fitness_metric == 'entropish_old'):
        if (var < .01): entropish = 0
        else: entropish = 1/math.pow(math.e, 1/var)
        fitness = 1 - entropish
        assert(fitness >= 0 and fitness <= 1)

    return fitness


def calc_directed(fitness_metric, up_in, up_out, down_in, down_out):
    assert(False)
    # shouldn't be using
    # currently experimenting with this

    if (fitness_metric == 'entropy_conserved'):

        Bs = [up_in,up_out]
        Ds = [down_in, down_out] #too lazy to change B,D syntax here
        S = [0,0] #ENTROPY [in,out[
        for i in range(2):
            B,D = Bs[i],Ds[i]

            if (B==0): H_B = 0
            else: H_B = -1*(B/(B+D)) * math.log(B/float(B+D),2)

            if (D==0): H_D = 0
            else: H_D = -1*(D/(B+D)) * math.log(D/float(B+D),2)

            S[i] = H_B + H_D

        Sin, Sout = S[0], S[1]

        return abs(Sin - Sout)


    elif (fitness_metric == 'mutual_info'):

        Bs = [up_in,up_out]
        Ds = [down_in, down_out] #too lazy to change B,D syntax here
        S = [0,0] #ENTROPY [in,out]
        for i in range(2):
            B,D = Bs[i],Ds[i]
            S[i] = shannon_entropy(B,D)
        Sin, Sout = S[0], S[1]

        tot = (Bs[0]+Ds[0])*(Bs[1]+Ds[1])
        if tot==0: Sboth = 0
        else:
            pr11 = Bs[0]*Bs[1]/tot
            pr10 = Bs[0]*Ds[1]/tot
            pr01 = Ds[0]*Bs[1]/tot
            pr00 = Ds[0]*Ds[1]/tot

            assert(pr11+pr10+pr01+pr00 < 1.2 and pr11+pr10+pr01+pr00 > .8) #leave room for rounding

            if pr11==0: H11 = 0
            else: H11 = -1 * pr11 * math.log(pr11, 2)
            if pr10==0: H10 = 0
            else: H10 = -1 * pr10 * math.log(pr10, 2)
            if pr01==0: H01 = 0
            else: H01 = -1 * pr01 * math.log(pr01, 2)
            if pr00==0: H00 = 0
            else: H00 = -1 * pr00 * math.log(pr00, 2)
            Sboth = H11+H10+H01+H00
        assert(Sboth >= 0 and Sboth <= 2)

        assert(Sin+Sout-Sboth >= -.2 and Sin+Sout-Sboth <= 1.2) #room for rounding
        return Sin+Sout-Sboth


    elif (fitness_metric == 'mutual_info_rev'):

        Bs = [up_in,up_out]
        Ds = [down_in, down_out] #too lazy to change B,D syntax here
        S = [0,0] #ENTROPY [in,out]
        for i in range(2):
            B,D = Bs[i],Ds[i]
            S[i] = shannon_entropy(B,D)
        Sin, Sout = S[0], S[1]

        tot = (Bs[0]+Ds[0])*(Bs[1]+Ds[1])
        if tot == 0: Sboth = 0
        else:
            pr11 = Bs[0]*Bs[1]/tot
            pr10 = Bs[0]*Ds[1]/tot
            pr01 = Ds[0]*Bs[1]/tot
            pr00 = Ds[0]*Ds[1]/tot

            assert(pr11+pr10+pr01+pr00 < 1.2 and pr11+pr10+pr01+pr00 > .8) #leave room for rounding

            if pr11==0: H11 = 0
            else: H11 = -1 * pr11 * math.log(pr11, 2)
            if pr10==0: H10 = 0
            else: H10 = -1 * pr10 * math.log(pr10, 2)
            if pr01==0: H01 = 0
            else: H01 = -1 * pr01 * math.log(pr01, 2)
            if pr00==0: H00 = 0
            else: H00 = -1 * pr00 * math.log(pr00, 2)
            Sboth = H11+H10+H01+H00
        assert(Sboth >= 0 and Sboth <= 2)

        assert(1-Sin+Sout-Sboth >= -.2 and 1-Sin+Sout-Sboth <= 1.2)
        return 1-Sin+Sout-Sboth


    else: print("ERROR in node_fitness.calc_directed(): unknown fitness metric: " + str(fitness_metric))


def shannon_entropy(up,down):
    if (up == 0): H_up = 0
    else: H_up = -1 * (up / (up + down)) * math.log2(up / float(up + down))

    if (down == 0):  H_down = 0
    else:  H_down = -1 * (down / (up + down)) * math.log2(down / float(up + down))

    return H_up + H_down
