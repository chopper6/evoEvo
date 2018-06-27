import math

def calc_undirected (fitness_metric, up, down):
    if (up+down==0): return 0

    elif (fitness_metric == 'info'):
        return 1-shannon_entropy(up,down)

    else: print("ERROR in node_fitness.calc_undirected(): unknown fitness metric: " + str(fitness_metric))


def calc_continuous (states, temp_switch):
    mean = sum(states)/len(states)
    var = 0

    for state in states:
        var += math.pow((mean-state),2)

    if var == 0:
        info = 1
        return info

    entropy = 0
    pdf_part = 1/math.sqrt(2*math.pi*var)
    for state in states:
        pr = pdf_part*math.exp(-math.pow((mean-state),2)/float(2*var)) #based on normal distribution

        if(temp_switch == 'logpr'): entropy -= math.log(pr)
        elif(temp_switch == 'prlogpr'): entropy -= pr*math.log(pr)
        else: assert(False)
        #I think, instead of pr*math.log(pr)
        #may be different log base, such as #states

    info = 1-entropy
    print("[node_fitness.py] info = " + str(info))
    assert(info >= 0 and info <= 1)

    return info, var


def calc_directed(fitness_metric, up_in, up_out, down_in, down_out):
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
