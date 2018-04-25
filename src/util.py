import random, os
#----------------------------------------------------------------------------  
def slash(path): #likely kp only
    return path+(path[-1] != '/')*'/'
#--------------------------------------------------------------------------------------------------
def flip():
    return random.choice([1,-1])
#--------------------------------------------------------------------------------------------------
def sample_p_elements (elements,p):
    return  random.sample(elements,p)
#--------------------------------------------------------------------------------------------------
def advice (M, samples, configs):

    advice_upon = configs['advice_upon']
    biased = boool(configs['biased'])

    advice = {}
    if not biased:
        for element in samples:
            if (advice_upon=='nodes'): advice[element]=flip()
            elif (advice_upon=='edges'):
                advice[str(element)] = flip()

    else:
        for element in samples:

            indiv_bias = retrieve_indiv_bias(element, M, configs)

            rand                = random.uniform(0,1)

            if (advice_upon=='nodes'): 
                if rand <= indiv_bias:
                    advice[element] = 1
                else:
                    advice[element] = -1

            elif (advice_upon=='edges'):
                if rand <= indiv_bias:
                    advice[str(element)] = 1
                else:
                    advice[str(element)] = -1

    
    return advice


# --------------------------------------------------------------------------------------------------
def single_advice(M, element, configs):

    biased = boool(configs['biased'])

    if not biased:
        advice = flip()

    else:

        biased_center = retrieve_indiv_bias(element, M, configs)

        rand = random.uniform(0, 1)
        # rand                = random.SystemRandom().uniform(0,1)

        if rand <= biased_center:  advice = 1
        else:  advice = -1

    assert(advice == 1 or advice == -1)

    return advice
#--------------------------------------------------------------------------------------------------

def cluster_print(output_dir, text):
    with open(output_dir + "/thread_out.txt", 'a') as file:
        file.write(str(text) + "\n")
        file.flush()
        file.close()
    print(text)


def cleanPaths(path):
    # ignore empty lines
    # ignore lines beginning with '#'
    # ignore lines enclosed by @ .. @
    # replaces $env_var with the actual value
    clean = []
    LINES = open(path,'r').readlines()
    inside_comment = False
    for i in range(len(LINES)):
        line = LINES[i].strip()
        if len(line)==0:
            continue
        if inside_comment:
            if line[0] == '@':
                inside_comment = False
        else:
            if line[0]=='@':
                inside_comment = True
                continue
            if line[0]!='#':
                clean.append(line)
    j=0
    for path in clean:
        Ds,i = path.split('/'), 0
        for d in Ds:
            if len(d.split('$'))>1:
                Ds[i]=os.getenv(d.split('$')[1])
            i+=1
        clean[j]='/'.join(Ds).replace('//','/')
        j+=1
    return clean

def boool(val):
    if (val == "True" or val=='true' or val==1 or val==True): return True
    elif (val == "False" or val=='false' or val==0 or val == False): return False
    else: print("ERROR util.boool(): unknown truth value for " + str(val))

def is_it_none(val):
    if (val == "None" or val=="none" or val==None or val==0): return None
    else: return 1


def test_stop_condition(size, gen, configs):
    # get configs
    stop_condition = configs['stop_condition']
    max_gen = int(configs['max_generations'])
    end_size = int(configs['ending_size'])
    output_dir = configs['output_directory']

    if (stop_condition == 'size'):
        if (size < end_size): cont = True
        else: cont = False
    elif (stop_condition == 'generation'):
        if (gen < max_gen): cont = True
        else: cont = False
    else:
        cluster_print(output_dir, "ERROR in master.test_stop_condition(): unknown stop_condition: " + str(stop_condition))
        return

    return cont


def retrieve_indiv_bias(element, M, configs):

    advice_upon = configs['advice_upon']
    bias_on = configs['bias_on']
    biased = boool(configs['biased'])

    if not biased: return .5

    if (advice_upon == 'nodes'):
        assert (bias_on == 'nodes') #not sure what advice on nodes, bias on edges would be represented as
        indiv_bias = M.node[element]['bias']

    elif (advice_upon == 'edges'):
        source = int(element[0])
        target = int(element[1])
        if (M.has_edge(source, target)):
            if (bias_on == 'nodes'):
                # this is one possible way to handle advice on edges, but bias on nodes
                indiv_bias = (M.node[source]['bias'] + M.node[target]['bias']) / 2
            elif (bias_on == 'edges'):
                indiv_bias = M[source][target]['bias']
            else:
                print("ERROR  util.advice(): unknown bias_on: " + str(bias_on))
                indiv_bias = False
        else:
            print("ERROR  util.advice(): could not find desired edge.\n")
            indiv_bias = False

    return indiv_bias
