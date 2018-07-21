import os, pickle, time, shutil, sys
from random import SystemRandom as sysRand
from time import sleep
import fitness, minion, output, plot_nets, build_nets, pressurize, util, init, bias, base_problem, reservoir

#MASTER EVOLUTION
def evolve_master(configs):
    # get configs
    output_dir = configs['output_directory']
    worker_pop_size = int(configs['num_worker_nets'])
    biased = util.boool(configs['biased'])
    num_sims = int(configs['num_sims'])
    net_base_problem = util.boool(configs['net_base_problem'])

    init_data = init_run(configs)
    if not init_data: return #for example if run already done

    population, teacher_net, dummy_net, gen, size, num_survive, keep_running = init_data

    while keep_running:
        t_start = time.time()
        pop_size, num_survive = curr_gen_params(size, num_survive, configs)

        write_mpi_info(output_dir, gen) #also writes progress file with relevant generation
        if net_base_problem: write_teacher_net(teacher_net, configs)

        if biased: biases = bias.gen_biases(configs) #all nets must have same bias to have comparable fitness
        else: biases = None

        if net_base_problem:
            problem_instances = base_problem.step_teacher_net(teacher_net, dummy_net, gen, configs)
        else: problem_instances = None

        distrib_workers(population, gen, worker_pop_size, num_survive, biases, problem_instances, configs)

        report_timing(t_start, gen, output_dir)
        population = watch(configs, gen, num_survive)

        size = len(population[0].nodes())
        output.master_info(population, gen, size, pop_size, num_survive, configs)

        gen += 1

        keep_running = util.test_stop_condition(size, gen, configs)

    output.final_master_info(population, gen, configs)
    del_mpi_dirs(output_dir)
    with open(output_dir + "/progress.txt", 'w') as out: out.write("Plotting")

    util.cluster_print(output_dir,"Evolution finished, generating images.")
    if (num_sims == 1): plot_nets.all_plots(configs)
    else: plot_nets.all_plots(configs, feature_plots=False)


    with open(output_dir + "/progress.txt", 'w') as out: out.write("Done.")
    util.cluster_print(output_dir,"Master finished config file.\n")






################################ INIT HELPER FUNCTIONS ################################
def init_run(configs):
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    start_size = int(configs['starting_size'])
    fitness_direction = str(configs['fitness_direction'])
    net_base_problem = util.boool(configs['net_base_problem']) #a teacher net is used for the base problem
    if net_base_problem: assert(not util.boool(configs['feedforward']))

    population, gen, size, keep_running = None, None, None, None #avoiding annoying warnings

    pop_size, num_survive = curr_gen_params(start_size, None, configs)
    util.cluster_print(output_dir,"Master init: num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))
    prog_path = output_dir + "/progress.txt"
    cont=False


    if os.path.isfile(prog_path):
        with open(prog_path) as file:
            gen = file.readline()

        if (gen == 'Done'):
            util.cluster_print(output_dir, "Run already finished, exiting...\n")
            return None

        elif (gen == 'Plotting'):

            util.cluster_print(output_dir, "####################### JUST PLOTTING #######################\n")

            util.cluster_print(output_dir, "Evolution finished, generating images.")
            if (num_sims == 1):
                plot_nets.all_plots(configs)
            else:
                plot_nets.all_plots(configs, feature_plots=False)

            return None


        elif (int(gen) > 2): #IS CONTINUATION RUN
            gen = int(gen)-2 #latest may not have finished
            population = parse_worker_popn(num_workers, gen, output_dir, num_survive, fitness_direction)
            if net_base_problem:
                teacher_net = parse_teacher_net(configs)
                dummy_net = build_nets.gen_a_rd_net(configs, size=len(population[0].nodes()))
            else: teacher_net, dummy_net = None, None

            size = len(population[0].nodes())
            gen += 1

            keep_running = util.test_stop_condition(size, gen, configs)
            cont = True
            util.cluster_print(output_dir, "####################### CONTINUATION RUN STARTING AT GEN " + str(gen) + "#######################\n")
        #else not cont runs

    if not cont: #FRESH START
        init_dirs(num_workers, output_dir)
        output.init_csv(output_dir, configs)
        # draw_nets.init(output_dir)

        population = build_nets.init_population(pop_size, configs)
        if net_base_problem:
            teacher_net = build_nets.gen_a_rd_net(configs, size=configs['teacher_net_size'])
            dummy_net = build_nets.gen_a_rd_net(configs)
            # TODO: if online learning, need to initiliaze teacher_net (and not reapply input at each gen)
            #reservoir.initialize_input(teacher_net, configs)
        else:
            teacher_net, dummy_net = None, None

        gen = 0
        keep_running = util.test_stop_condition(start_size, gen, configs)

    #init_data =  population, teacher_net, gen, size, num_survive, keep_running
    return [population, teacher_net, dummy_net, gen, size, num_survive, keep_running]


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dirs = ["/nets_nx/", "/bias/", "/to_workers/", "/to_master/", "/nets_pickled/", "/base_problem/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir+dirr)


################################ MPI-RELATED HELPER FUNCTIONS ################################
def write_mpi_info(output_dir, gen):

    with open(output_dir + "/progress.txt", 'w') as out:
        out.write(str(gen))
    #util.cluster_print(output_dir, 'Master wrote progress.txt, now checking dir: ' + str(output_dir + "/to_workers/" + str(itern)))
    if not os.path.exists(output_dir + "/to_workers/" + str(gen)):
        os.makedirs(output_dir + "/to_workers/" + str(gen))
    if not os.path.exists(output_dir + "/to_master/" + str(gen)):
        os.makedirs(output_dir + "/to_master/" + str(gen))

    #del old gen dirs
    prev_gen = gen - 3 #safe since cont starts at itern - 2
    if os.path.exists(output_dir + "/to_master/" + str(prev_gen)):
        shutil.rmtree(output_dir + "/to_master/" + str(prev_gen))
    if os.path.exists(output_dir + "/to_workers/" + str(prev_gen)):
        shutil.rmtree(output_dir + "/to_workers/" + str(prev_gen))


def distrib_workers(population, gen, worker_pop_size, num_survive, biases, problem_instances, configs):
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    debug = util.boool(configs['debug'])

    for w in range(1, num_workers + 1):
        dump_file = output_dir + "/to_workers/" + str(gen) + "/" + str(w)
        seed = population[w % num_survive].copy()
        randSeeds = os.urandom(sysRand().randint(0, 1000000))
        assert (seed != population[w % num_survive])
        worker_args = [w, seed, worker_pop_size, min(worker_pop_size, num_survive), randSeeds, biases, problem_instances, configs]
        with open(dump_file, 'wb') as file:
            pickle.dump(worker_args, file)
        if (debug == True):  # sequential debug
            minion.evolve_minion(dump_file, gen, w, output_dir) # calls minion from same thread
            sleep(.0001)
        # else minions are already running as sep threads

    del population
    if (debug == True and gen % 10 == 0): util.cluster_print(output_dir, "debug is ON")


def parse_worker_popn (num_workers, gen, output_dir, num_survive, fitness_direction):
    popn = []
    print('master.parse_worker_popn(): num workers = ' + str(num_workers) + " and gen " + str(gen))
    print("parse worker pop params: dir = " + str(output_dir) + ".")
    for w in range(1,num_workers+1): 
        dump_file = output_dir + "/to_master/" + str(gen) + "/" + str(w)
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        i=0
        for indiv in worker_pop:
            popn.append(indiv)
            i+=1

    sorted_popn = fitness.eval_fitness(popn, fitness_direction)
    return sorted_popn[:num_survive]

def parse_teacher_net(configs):
    output_dir = configs['output_directory']

    teacher_file = output_dir + "teacher_net"
    with open(teacher_file, 'rb') as file:
        teacher_net = pickle.load(file)

    return teacher_net

def write_teacher_net(teacher_net, configs):
    output_dir = configs['output_directory']
    teacher_file = output_dir + "teacher_net"

    with open(teacher_file, 'wb') as file:
        pickle.dump(teacher_net, file)


def watch(configs, gen, num_survive):

    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    fitness_direction = str(configs['fitness_direction'])
    debug = util.boool(configs['debug'])

    dump_dir = output_dir + "/to_master/" + str(gen)
    t_start = time.time()
    popn, num_finished, dir_checks = [], 0,0

    ids = [str(i) for i in range(1, num_workers + 1)]
    while (num_finished < num_workers):
        time.sleep(1)
        dir_checks+=1
        for root, dirs, files in os.walk(dump_dir):
            for f in files:
                if f in ids:
                        if (os.path.getmtime(root + "/" + f) + 1 < time.time()):
                            dump_file = output_dir + "/to_master/" + str(gen) + "/" + str(f)
                            with open(dump_file, 'rb') as file:
                                try:
                                    worker_pop = pickle.load(file)
                                    popn += worker_pop[:num_survive]
                                    num_finished += 1
                                    ids.remove(f)
                                except: pass

            #sort and delete some
            sorted_popn = fitness.eval_fitness(popn, fitness_direction)
            popn = sorted_popn[:num_survive]
            del sorted_popn
    assert (not ids)

    t_end = time.time()
    time_elapsed = t_end - t_start
    if (gen % 100 == 0): util.cluster_print(output_dir,"master finished extracting workers after " + str(time_elapsed) + " seconds, and making " + str(dir_checks) + " dir checks.")

    return popn


def del_mpi_dirs(output_dir):
    shutil.rmtree(output_dir + "/to_master/")
    shutil.rmtree(output_dir + "/to_workers/")


################################ MISC HELPER FUNCTIONS ################################
def curr_gen_params(size, prev_num_survive, configs):
    #could add dynam worker_pop_size Island algo and such
    num_workers = int(configs['number_of_workers'])
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    worker_pop_size = int(configs['num_worker_nets'])

    pop_size = worker_pop_size * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):  num_survive = 1
    if (prev_num_survive):
        if (num_survive > prev_num_survive): num_survive = prev_num_survive

    return pop_size, num_survive


def report_timing(t_start, gen, output_dir, report_freq=.001):
    if report_freq == 0: return
    t_end = time.time()
    t_elapsed = t_end - t_start
    if (gen % int(1 / report_freq) == 0): util.cluster_print(output_dir, "Master finishing after " + str(t_elapsed) + " seconds.\n")



if __name__ == "__main__":
    # note that phone calls this directly
    # could add a base dirr to make arg1 shorter

    rank = 0 #ie master only

    config_file = sys.argv[1]
    num_workers = sys.argv[2]

    configs = init.load_sim_configs(config_file, rank, num_workers)
    orig_output_dir = configs['output_directory']
    num_sims = int(configs['num_sims'])
    assert(num_sims == 1) #not ready for more
    assert(configs['debug'] == True) #otherwise need more workers

    log_text = 'Evolve_root(): in dir ' + str(os.getcwd()) + ', config file = ' + str(config_file) + ', num_workers = ' + str(num_workers) + "\n"

    util.cluster_print(configs['output_directory'], log_text)
    evolve_master(configs)

    print("\nDone.\n")
