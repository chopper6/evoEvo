# worker processes
import pickle, random, os, time
import output, fitness, pressurize, mutate, init, util

#################### PARALLELISM FUNCTIONS ####################
def work(configs, rank):
    output_dir = configs['output_directory']
    progress_file = output_dir + "/progress.txt"

    print ("\t\t\t\tworker #"+str(rank)+" is working,\t")

    gen = read_progress_file(progress_file, output_dir, rank)

    estim_time = 4
    keep_running = True
    while keep_running:
        worker_file = str(output_dir) + "/to_workers/" + str(gen) + "/" + str(rank)
        estim_time = wait_for_worker_file(worker_file, estim_time, gen, output_dir, rank)
        size = evolve_minion(worker_file, gen, rank, output_dir)
        gen+=1
        keep_running = util.test_stop_condition(size, gen, configs)



def read_progress_file(progress, output_dir, rank):
    t_start = time.time()
    while not os.path.isfile(progress):  # master will create this file
        time.sleep(2)

    while not (os.path.getmtime(progress) + 2 < time.time()):  # check that file has not been recently touched
        time.sleep(2)

    with open(progress, 'r') as file:
        line = file.readline()
        if (line == 'Done' or line == 'Done\n'):
            if (rank == 1 or rank==32 or rank==63): util.cluster_print(output_dir,"Worker #" + str(rank) + " + exiting.")
            return  # no more work to be done
        else:
            gen = int(line.strip())

    t_end = time.time()
    #if ((rank == 1 or rank == 63 or rank == 128) and gen % 100 == 0): util.cluster_print(output_dir,"worker #" + str(rank) + " finished init in " + str(t_end-t_start) + " seconds.")
    return gen

def wait_for_worker_file(worker_file, estim_time, gen, output_dir, rank):
    t_start = time.time()
    # util.cluster_print(output_dir,"worker #" + str(rank) + " looking for file: " + str(worker_file))
    i = 1
    num_estim = 0
    while not os.path.isfile(worker_file):
        if (num_estim < 4):
            time.sleep(estim_time / 4)
            num_estim += 1
        else:
            time.sleep(4)
            estim_time += 4
        i += 1
    estim_time /= 2

    while not (os.path.getmtime(worker_file) + 1 < time.time()):
        time.sleep(1)

    t_end = time.time()
    t_elapsed = t_end - t_start
    #if ((rank == 1 or rank == 63 or rank == 128) and gen % 100 == 0): util.cluster_print(output_dir, "Worker #" + str(rank) + " starting evolution after waiting " + str(t_elapsed) + " seconds and checking dir " + str(i) + " times. Starts at gen " + str(gen))
    return estim_time



#################### EVOLUTION FUNCTIONS ####################
def evolve_minion(worker_file, gen, rank, output_dir):
    t_start = time.time()

    worker_ID, seed, pop_size, num_return, randSeed, advice,  biases, configs = load_worker_file(worker_file)
    output_dir, fitness_direction, population = init_minion(configs, randSeed, seed, pop_size)

    for p in range(pop_size):

        #temp
        assert(p.graph['input_nodes'][0] != None)
        assert(p.graph['output_nodes'][0] != None)
        mutate.mutate(configs, population[p], biases=biases)
        pressurize.pressurize(configs, population[p], advice)

    population = sort_popn(population, fitness_direction)
    write_out_worker(output_dir + "/to_master/" + str(gen) + "/" + str(rank), population, num_return)
    report_timing(t_start, rank, gen, output_dir)

    return len(population[0].nodes())



def load_worker_file(worker_file):

    loaded = False
    with open(str(worker_file), 'rb') as file:
        while (loaded==False):
            try:
                worker_ID, seed, pop_size, num_return, randSeed, advice, biases, configs = pickle.load(file)
                loaded = True
            except EOFError: time.sleep(2)
        file.close()

    return worker_ID, seed, pop_size, num_return, randSeed, advice, biases, configs


def init_minion(configs, randSeed, seed, pop_size):
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    fitness_direction = str(configs['fitness_direction'])
    random.seed(randSeed)
    population = gen_population_from_seed(seed, pop_size)

    return output_dir, fitness_direction, population


def gen_population_from_seed(seed, num_survive):
    population = []
    for p in range(num_survive):
        population.append(seed.copy())
        assert(population[-1] != seed)
    return population


def sort_popn(population, fitness_direction):
    old_popn = population
    population = fitness.eval_fitness(old_popn, fitness_direction)
    del old_popn
    return population


def write_out_worker(worker_file, population, num_return):
    # overwrite own input file with return population
    with open(worker_file, 'wb') as file:
        pickle.dump(population[:num_return], file)
        file.close()


def report_timing(t_start, rank, gen, output_dir):
    t_end = time.time()
    time_elapsed = t_end - t_start
    if ((rank == 1 or rank==63) and gen % 100 == 0): util.cluster_print(output_dir,"Worker #" + str(rank) + " finishing after " + str(time_elapsed) + " seconds")
