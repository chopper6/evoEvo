import os
# poss replace all these
import util, build_nets, output, plot_nets

#MASTER EVOLUTION
def evolve_master(configs):
    # get configs
    output_dir = configs['output_directory']

    init_dirs(output_dir)
    net = build_nets.basic_distributed(configs)
    keep_running, gen = True, 0

    while keep_running:

        # evo an iteration
        activate_nodes(net)

        output.evoBit_data(net, gen, configs) #TODO: build this

        gen += 1
        keep_running = util.test_stop_condition(len(net.nodes()), gen, configs)

    output.evoBit_data(net, gen, configs) #TODO
    util.cluster_print(output_dir,"Evolution finished, generating images.")

    plot_nets.all_plots(configs) #TODO check but should be similar

    util.cluster_print(output_dir,"Done.\n")




def init_dirs(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dirs = ["/nets_nx/", "/bias/", "/to_workers/", "/to_master/", "/nets_pickled/", "/base_problem/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir+dirr)


def activate_nodes(net):
    for n in net.nodes():




################################ MISC HELPER FUNCTIONS ################################



if __name__ == "__main__":
    # note that yamaska and rupert should call this directly
    # guillimin calls through batch_root
    config_file = sys.argv[1]
    evolve(config_file)

