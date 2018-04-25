#from scipy.special import comb as nchoosek
import math, numpy as np, networkx as nx, pickle, os
log10 = math.log10
def l1(s):
    return str(s).ljust(10,' ')
def l(s):
    return str(s).ljust(7,' ')
################################### Fitness function #########################################
def unambiguity_fitness_score(G): # G is a networkx DiGraph (one of your population of networks)
    n2e     = 0.5
    e2n     = 2.0
    p       = .5 
    q       = 1 - p
    fitness = []
    for d in G.degree().values():
        if d == 0:
            fitness.append(0)
            continue
        if d>300:
            d = 300
        unambiguity = []
        for k in range(0,d+1,1):
            #dCk          = nchoosek(d,k,exact=True)
            dCk = math.factorial(d)/float(math.factorial(k)*math.factorial(d-k))
            count        = dCk   *   p**k   *   q**(d-k)
            unambiguity.append(n2e*(count**(e2n*log10(d)))) # winner
        fitness.append(np.average(unambiguity))
    return np.average(fitness)
###############################################################################################


