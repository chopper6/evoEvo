#!/usr/bin/python3
import matplotlib, os, sys, numpy as np, networkx as nx, math, re, pickle
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt, matplotlib.patches as mpatches
from decimal import Decimal
import util


################## ORGANIZER FUNCTIONS ##################
def all_plots (configs, feature_plots=True, indiv_plots = True, orig_output_directory=None, var = False):

    if orig_output_directory: dirr = orig_output_directory
    else: dirr = configs['output_directory']
    #plots features_over_time and degree_distrib
    #only uses most fit indiv in population
    if not os.path.exists(dirr):
        print("ERROR plot_nets(): given directory not found: " + str(dirr))
        return

    if feature_plots:
        if var: net_info, net_info_var, titles = parse_info(dirr, var=var)
        else: net_info, titles = parse_info(dirr)

        img_dirs = ["/images_by_size/", "/images_by_time/", "/images_by_time_logScaled/"]
        for img_dir in img_dirs:
            if not os.path.exists(dirr + img_dir):
                os.makedirs(dirr + img_dir)

        mins, maxs = 0,0
        features_over_size(dirr, net_info, titles, mins, maxs, False)
        if var: features_over_time(dirr, net_info, titles, mins, maxs, False, var_data=net_info_var)
        else: features_over_time(dirr, net_info, titles, mins, maxs, False)

    if indiv_plots:
        print("Generating directed degree distribution plots.")
        degree_distrib(dirr)

        print("Generating base error plots.")
        base_problem_features(dirr, configs)

        print("Generating undirected degree distribution plots.")
        plot_undir(configs) #last two args for Biased and bias on, which haven't really been implemented

        print("Generating degree change plot.\n")
        degree_distrib_change(dirr) #may require debugging



def plot_undir(configs):

    output_dir = configs['output_directory']
    biased, bias_on = False, None #not implemented yet

    dirs = ["/undirected_degree_distribution/"]

    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir + dirr)

    for root, dirs, files in os.walk(output_dir + "/nets_pickled/"):
        for f in files:
            #print("plot_dir(): file " + str(f))
            undir_deg_distrib(root + "/" + f, output_dir + "/undirected_degree_distribution/", f, biased, bias_on, configs)
            #LATER: variance_and_entropy_distrib(root + "/" + f, output_dir, f)


################## IMAGE GENERATION FUNCTIONS ##################

def variance_and_entropy_distrib(net_file, destin_dir, title):

    net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())

    color_choice = 'purple'

    for feature in ['info','variance']:
        H = []
        vals = []
        for n in net.nodes():
            if (feature == 'info'): vals.append(net.node[n]['fitness']) #note that may not be recorded in edgelist
            elif (feature == 'variance'): vals.append(net.node[n]['var'])

    #not sure what to plot yet...
    return



def undir_deg_distrib(net_file, destin_path, title, biased, bias_on, configs):

    if (re.match(re.compile("[a-zA-Z0-9]*pickle"), net_file)):
        with open(net_file, 'rb') as file:
            net = pickle.load(file)
            file.close()
    else:
        #net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())
        with open(net_file, 'rb') as file:
            net = pickle.load(file)

    colors = ['#0099cc','#ff5050', '#6699ff']
    color_choice = colors[0]

    reservoir_nodes = []
    if util.boool(configs['directed']):
        for n in net.nodes():
            if net.node[n]['layer'] == 'hidden': reservoir_nodes.append(
                n)  # this will throw an error if undirected version
    else:
        for n in net.nodes(): reservoir_nodes.append(n)

    for type in ['loglog%']: #can also use ['loglog', 'scatter', 'scatter%']
        H = []
        #loglog
        degrees = list(net.degree(reservoir_nodes).values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        if (type=='loglog%' or type=='scatter%'): freqs = [(f/tot)*100 for f in freqs]

        #derive vals from conservation scores
        bias_vals, ngh_bias_vals = [], []
        if (biased == True or biased == 'True'):
            for deg in degs: #deg bias is normalized by num nodes
                avg_bias, ngh_bias, num_nodes = 0,0,0
                for node in net.nodes():
                    if (net.degree(node) == deg):
                        if (bias_on == 'nodes'):
                            avg_bias += abs(.5-net.node[node]['bias'])

                            avg_ngh_bias = 0
                            for ngh in net.neighbors(node):
                                avg_ngh_bias += net.node[ngh]['bias']
                            avg_ngh_bias /= len(net.neighbors(node))
                            ngh_bias += abs(.5-avg_ngh_bias)

                        elif (bias_on == 'edges'): #node bias is normalized by num edges
                            node_bias, num_edges = 0, 0
                            for edge in net.edges(node):
                                node_bias += net[edge[0]][edge[1]]['bias']
                                num_edges += 1
                            if (num_edges != 0): node_bias /= num_edges
                        num_nodes += 1
                avg_bias /= num_nodes
                ngh_bias /= num_nodes
                bias_vals.append(avg_bias)
                ngh_bias_vals.append(ngh_bias)
            assert(len(bias_vals) == len(degs))

            with open(destin_path + "/degs_freqs_bias_nghBias",'wb') as file:
                pickle.dump(file, [degs, freqs, bias_vals, ngh_bias_vals])


            cmap = plt.get_cmap('plasma')
            bias_colors = cmap(bias_vals)

            if (type == 'loglog' or type=='loglog%'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, c = bias_colors, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter' or type=='scatter%'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, c = bias_colors, alpha=1, s=sizes, marker='D')

        else:
            if (type == 'loglog' or type=='loglog%'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = color_choice, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter' or type=='scatter%'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, color = color_choice, alpha=1, s=sizes, marker='D')
        patch =  mpatches.Patch(color=color_choice, label=title + "_" + type)
        H = H + [patch]

        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance

        if (type == 'loglog%' or type=='scatter%'):
            ax.set_xlim([0,100])
            ax.set_ylim([0,100])
        elif (type == 'loglog' or type == 'scatter'):
            max_x = max(1,math.floor(max(degs)/10))
            max_x = max_x*10+10

            max_y = max(1,math.floor(max(freqs)/10))
            max_y = max_y*10+100

            upper_lim = max(max_x, max_y)

            ax.set_xlim([0, upper_lim])
            ax.set_ylim([0, upper_lim])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
        plt.xlabel('Degree')
        if (type=='loglog%'): plt.ylabel('Percent of Nodes with Given Degree')
        else: plt.ylabel('Number of Nodes with Given Degree')
        #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

        plt.tight_layout()
        plt.savefig(destin_path + "/" + type + "_" + title + ".png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
        plt.clf()
        plt.cla()
        plt.close()



def base_problem_features(dirr, configs):

    for feature_name in ['error', 'fitness']:
        file_name = dirr + "/base_problem/" + str(feature_name) + ".csv"

        all_lines = [Line.strip() for Line in (open(file_name, 'r')).readlines()]
        #titles = all_lines[0]

        i, curr_gen, t, feature = 0, 0, [], []

        line = all_lines[0]
        line = line.replace('[', '').replace(']', '').replace("\n", '')
        line = line.split(',')
        feature_description = line[2]

        for line in all_lines[1:]:

            line = line.replace('[', '').replace(']', '').replace("\n", '')
            line = line.split(',')
            a_feature = line[2]
            if a_feature != None and a_feature != "None" and a_feature:
                gen = int(line[0])
                if gen != curr_gen:
                    # PLOT AND RESET
                    # plot before appending current line, since that is for diff gen
                    one_base_feature_plot(dirr, feature, t, curr_gen, feature_name, feature_description)
                    # reset for next plot
                    curr_gen, i, t, feature = gen, 0, [], []

                feature.append(float(a_feature))
                t.append(i)

                i += 1

        # plot last recorded gen
        one_base_feature_plot(dirr, feature, t, curr_gen, feature_name,  feature_description)


def one_base_feature_plot(dirr, feature, t, curr_gen, title,  feature_description):

    # trimming number of data points
    if len(feature) > 40:
        x, y = [], []
        for j in range(len(feature)):
            if (j % int(len(feature) / 40)) == 0:
                x.append(t[j])
                y.append(feature[j])
    else:
        x = t
        y = feature

    if len(x) > 11:
        xticks = [int(j * x[-1] / 10) for j in range(11)]
        #xlabels = [x[xtick] for xtick in xticks]
    else:
        xticks = x

    plt.plot(x, y)

    plt.ylabel(str(feature_description))
    plt.title("Gen " + str(curr_gen) + " Base Problem " + str(title))
    plt.xlabel("Iteration")
    plt.xticks(xticks, xticks)
    plt.savefig(dirr + "/base_problem/" + str(title) + "_gen" + str(curr_gen) + ".png")
    plt.clf()



def degree_distrib(dirr):
        deg_file_name = dirr + "/degree_distrib.csv"

        if not os.path.exists(dirr + "/directed_degree_distribution/"):
            os.makedirs(dirr + "/directed_degree_distribution/")

        all_lines = [Line.strip() for Line in (open(deg_file_name,'r')).readlines()]
        titles = all_lines[0]
        img_index = 0
        for line in all_lines[1:]:
            line = line.replace('[', '').replace(']','').replace("\n", '')
            line = line.split(',')
            gen = line[0]
            in_deg = line[2].split(" ")
            in_deg_freq = line[3].split(" ")
            out_deg = line[4].split(" ")
            out_deg_freq = line[5].split(" ")

            in_deg = list(filter(None, in_deg))
            in_deg_freq = list(filter(None, in_deg_freq))
            out_deg = list(filter(None, out_deg))
            out_deg_freq = list(filter(None, out_deg_freq))

            # plot in degrees
            plt.loglog(in_deg, in_deg_freq, basex=10, basey=10, linestyle='', color='blue', alpha=0.7, markersize=7, marker='o', markeredgecolor='blue')

            #plot out degrees on same figure
            plt.loglog(out_deg, out_deg_freq, basex=10, basey=10, linestyle='', color='green', alpha=0.7, markersize=7, marker='D', markeredgecolor='green')

            #way to not do every time?
            ax = matplotlib.pyplot.gca()
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
                axis='both',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                right='off',  # ticks along the right edge are off
                top='off',  # ticks along the top edge are off
            )
            in_patch = mpatches.Patch(color='blue', label='In-degree')
            out_patch = mpatches.Patch(color='green', label='Out-degree')
            plt.legend(loc='upper right', handles=[in_patch, out_patch], frameon=False)
            plt.xlabel('Degree (log) ')
            plt.ylabel('Number of nodes with that degree (log)')
            plt.title('Degree Distribution of Fittest Net at Generation ' + str(gen))
            plt.xlim(1,1000)
            plt.ylim(1,1000)
            plt.savefig(dirr + "/directed_degree_distribution/" + str(gen) + ".png", dpi=300)
            plt.clf()
            img_index += 1


def features_over_size(dirr, net_info, titles, mins, maxs, use_lims):
    #size is 2nd col of net info

    img_dirr = dirr + "/images_by_size/"
    for i in range(len(titles)):
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j,i])
            xdata.append(net_info[j,1])
        x_ticks = []
        max_net_size = max(xdata)
        for j in range(0,11):
            x_ticks.append((max_net_size/10)*j)
        plt.plot(xdata, ydata)
        plt.ylabel(titles[i] + " of most fit Individual")
        plt.title(titles[i])
        if (use_lims==True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Net Size")
        plt.xticks(x_ticks, x_ticks)
        plt.savefig(img_dirr + str(titles[i]) + ".png")
        plt.clf()
    return


def degree_distrib_change(dirr):
    deg_file_name = dirr + "/degree_distrib.csv"

    if not os.path.exists(dirr + "/degree_distribution_change/"):
        os.makedirs(dirr + "/degree_distribution_change/")

    all_lines = [Line.strip() for Line in (open(deg_file_name, 'r')).readlines()]
    titles = all_lines[0]

    # Get starting degree distribution
    line = all_lines[1]
    line = line.replace('[', '').replace(']', '').replace("\n", '')
    line = line.split(',')
    deg = line[6].split(" ")
    deg_freq = line[7].split(" ")
    start_deg = list(filter(None, deg))
    start_freq = list(filter(None, deg_freq))

    # Get ending degree distribution
    line = all_lines[-1]
    line = line.replace('[', '').replace(']', '').replace("\n", '')
    line = line.split(',')
    deg = line[6].split(" ")
    deg_freq = line[7].split(" ")
    end_deg = list(filter(None, deg))
    end_freq = list(filter(None, deg_freq))

    start_col = '#ff5050'
    end_col = '#0099cc'

    plt.loglog(start_deg, start_freq, basex=10, basey=10, linestyle = '', c=start_col, alpha=0.8, markersize=7, marker='o')
    plt.loglog(end_deg, end_freq, basex=10, basey=10, linestyle='', c=end_col, alpha=0.8, markersize=7, marker='o')
    #plt.scatter(end_deg, end_freq, c=end_col, alpha=0.8, s=40, marker='o')

    ax = matplotlib.pyplot.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim([1,1000])
    ax.set_ylim([1,1000])

    plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        right='off',  # ticks along the right edge are off
        top='off',  # ticks along the top edge are off
    )
    in_patch = mpatches.Patch(color=start_col, label='Initial Degree Frequency')
    out_patch = mpatches.Patch(color=end_col, label='Final Degree Frequency')
    plt.legend(loc='upper right', handles=[in_patch, out_patch], frameon=False)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes with Given Degree')
    plt.title('Change in Degree Distribution')
    plt.savefig(dirr + "/degree_distribution_change/in_degree_change.png", dpi=300)
    plt.clf()


def features_over_time(dirr, net_info, titles, mins, maxs, use_lims, var_data=None):
    img_dirr = dirr + "/images_by_time/"
    logscaled_img_dirr = dirr + "/images_by_time_logScaled/"

    # regular images
    for i in range(len(titles)):
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j, i])
            xdata.append(net_info[j, 0])

        max_gen = xdata[-1]
        x_ticks = [int((max_gen / 10) * j) for j in range(11)]


        if var_data is None: plt.plot(xdata, ydata)
        else:
            assert(len(var_data) == len(net_info))
            assert(len(var_data[0]) == len(net_info[0]))
            y_var = []
            for j in range(num_outputs):
                y_var.append(var_data[j, i])

            plt.errorbar(xdata,ydata,yerr=y_var, linewidth=2, elinewidth=.5, capsize=4, capthick = 2)

        plt.ylabel(titles[i])
        plt.title(titles[i])
        if (use_lims == True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Generation")
        plt.xticks(x_ticks, x_ticks)
        plt.savefig(img_dirr + str(titles[i]) + ".png")
        plt.clf()

        # logScaled images, may not always make sense
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j, i])
            xdata.append(net_info[j, 0])

        ydata2 = []
        for y in ydata:
            if (y==0): ydata2.append(0)
            elif(y<0): ydata2.append(-100)
            else: ydata2.append(Decimal(math.log(Decimal(y),10)))
        ydata = ydata2

        x_ticks = []
        max_gen = xdata[-1]
        for j in range(0, 11):
            x_ticks.append(int((max_gen / 10) * j))

        plt.plot(xdata, ydata)

        plt.ylabel(titles[i])
        plt.title(titles[i])
        if (use_lims == True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Generation")
        plt.xticks(x_ticks, x_ticks)

        plt.savefig(logscaled_img_dirr + str(titles[i]) + ".png")
        plt.clf()


    return


def comparison_plots(dirr):

    data, run_names, var_data = [], [], []
    var_exists = False
    titles = None
    #colors = ['red', 'blue', 'green', 'magenta', 'cyan']
    colors = ['#cc0066', '#006699', '#6600ff', '#ff9900', '#33cc33', '#009933', '#0000ff', '#cc00cc', '#663300', '#666633']

    if os.path.exists(dirr):

        for root, dirs, files in os.walk(dirr + "/"):
            for d in dirs:
                net_file_exists, net_var_exists = False, False
                for root, dirs, files in os.walk(dirr + "/" + d):
                    for f in files:
                        if f == 'net_data.csv': net_file_exists = True
                        if f == 'net_data_variance.csv':  
                            net_var_exists = True
                            var_exists = True

                if net_file_exists:
                    if net_var_exists:
                        net_info, net_info_var, titles = parse_info(dirr + "/" + d, var=True)
                        var_data.append(net_info_var)
                    else: net_info, titles = parse_info(dirr + "/" + d)
                    data.append(net_info)
                    name = d
                    run_names.append(name)


    else: assert(False) #cannot find directory

    assert(len(titles) > 0) #otherwise couldn't find anything to fill data with (net_data.csv DNE?)
    if var_exists: assert(len(data) == len(var_data)) #otherwise complicates things

    if not os.path.exists(dirr + "/comparison_plots/"):
        os.makedirs(dirr + "/comparison_plots/")

    last_net_info = net_info
    for i in range(len(titles)):

        xdata, legend_pieces = [], []

        for k in range(len(data)): #i.e. for each run
            net_info = data[k]
            if var_exists: var_info = var_data[k]
            assert(len(net_info) == len(last_net_info)) #checking dim

            num_outputs = len(net_info)
            ydata = []
            xdata = []
            for j in range(num_outputs):
                ydata.append(net_info[j, i])
                xdata.append(net_info[j, 0])

            color_choice = colors[k % len(colors)]

            if not var_exists:
                plt.plot(xdata, ydata, color=color_choice)
            else:
                assert (len(var_data) == len(data))
                assert (len(var_data[0]) == len(data[0]))
                y_var = []
                for j in range(num_outputs):
                    y_var.append(var_info[j, i])

                plt.errorbar(xdata, ydata, yerr=y_var, color=color_choice, linewidth=2, elinewidth=.5, capsize=4, capthick = 2)

            patch = mpatches.Patch(color=color_choice, label=run_names[k])
            legend_pieces.append(patch)

        max_gen = xdata[-1]
        x_ticks = [int((max_gen / 10) * j) for j in range(11)]
        plt.ylabel(titles[i])
        plt.title(titles[i])
        #if (use_lims == True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Generation")
        plt.xticks(x_ticks, x_ticks)

        plt.legend(loc='best', handles=legend_pieces)

        plt.savefig(dirr + "/comparison_plots/" + str(titles[i]) + ".png")
        plt.clf()


    return






################## HELPER FUNCTIONS ##################
def parse_info(dirr, var = False):
    #returns 2d array of outputs by features
    #note that feature[0] is the net size

    with open(dirr + "/net_data.csv", 'r') as info_csv:
        lines = info_csv.readlines()
        titles = lines[0].split(",")
        piece = titles[-1].split("\n")
        titles[-1] = piece[0]
        num_features = len(titles)
        num_output = len(lines)-1
        master_info = np.empty((num_output, num_features))

        for i in range(0,num_output):
            row = lines[i+1].split(",", num_features) 
            piece = row[-1].split("\n")
            row[-1] = piece[0]
            master_info[i] = row

    if var:
        with open(dirr + "/net_data_variance.csv", 'r') as info_csv:
            lines = info_csv.readlines()
            titles = lines[0].split(",")
            piece = titles[-1].split("\n")
            titles[-1] = piece[0]
            num_features = len(titles)
            num_output = len(lines) - 1
            master_info_var = np.empty((num_output, num_features))

            for i in range(0, num_output):
                row = lines[i + 1].split(",", num_features)
                piece = row[-1].split("\n")
                row[-1] = piece[0]
                master_info_var[i] = row

        assert(len(master_info) == len(master_info_var))
        return master_info, master_info_var, titles

    else: return master_info, titles


if __name__ == "__main__":
    #first bash arg should be parent directory, then each child directory
    base_dir = "/home/2014/choppe1/Documents/evoEvo/data/output/"

    if sys.argv[1] == 'comparison': #poss needs to be updated
        dirr = sys.argv[2]
        comparison_plots(base_dir + dirr)

    elif sys.argv[1] == 'undir':
        biased = None
        bias_on = None

        parent_dir = sys.argv[1]

        for dirr in sys.argv[2:]:
            print("plotting " + base_dir + parent_dir + dirr)
            plot_undir(base_dir + parent_dir + dirr, biased, bias_on)

    else: #default
        dirr_parent = sys.argv[1]
        base_dir += dirr_parent

        for arg in sys.argv[2:]:
            print("Plotting dirr " + str(arg))
            dirr_addon = arg
            dirr= base_dir + dirr_addon
            single_run_plots(dirr)

