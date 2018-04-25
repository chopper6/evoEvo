import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import matplotlib.pyplot as plt, matplotlib.patches as mpatches, matplotlib.ticker as ticker, matplotlib.font_manager as font_manager
import sys, os, networkx as nx, numpy as np, math, re, random as rd
from matplotlib import rcParams

def plot_pairs(real_net_file, real_net_name, sim_net_file, plot_title):
    input_files = open(real_net_file,'r').readlines()

    colors = ['#4C0099', '#006699','#009931','#990055', '#4C0099', '#ff0066', '#ffb31a', 'purple']
    i=0
    for line in input_files:
        name, network_file = line.strip().split(' ')
        if (name==real_net_name or real_net_name == 'all'):
            color_choice = colors[i%8]
            ymin, xmax = .02, 400

            color_by = 'org'

            if color_by == 'org':
                if (re.match(re.compile("[a-zA-Z0-9]*Human"), name)):
                    color_choice = colors[0]
                    name = name.replace('Human', ' Human')
                elif (re.match(re.compile("[a-zA-Z0-9]*Yeast"), name)):
                    color_choice = colors[1]
                    name = name.replace('Yeast', ' Yeast')
                elif (re.match(re.compile("[a-zA-Z0-9]*Mouse"), name)):
                    color_choice = colors[2]
                    name = name.replace('Mouse', ' Mouse')
                elif (re.match(re.compile("[a-zA-Z0-9]*Bacteria"), name)):
                    color_choice = colors[3]
                    name = name.replace('Bacteria', ' Bacteria')
                elif (re.match(re.compile("[a-zA-Z0-9]*TRRUST"), name)):
                    color_choice = colors[5]
                    name = name.replace('TRRUST', ' TRRUST')
                    ymin, xmax = .02, 500
                elif (re.match(re.compile("[a-zA-Z0-9]*Mi"), name)):
                    color_choice = colors[6]
                    name = name.replace('Mi', ' miRT')
                    ymin, xmax = .02, 210
                else:
                    color_choice = colors[7]


            elif color_by == 'context':
                if (re.match(re.compile("[a-zA-Z0-9]*PPI"), name)):
                    color_choice = colors[0]
                    name = name.replace('PPI', ' PPI')
                elif (re.match(re.compile("[a-zA-Z0-9]*BG"), name)):
                    color_choice = colors[1]
                    name = name.replace('BG', ' BioGrid')
                elif (re.match(re.compile("[a-zA-Z0-9]*PQ"), name)):
                    color_choice = colors[2]
                    name = name.replace('PQ', ' PSICQUIC')
                elif (re.match(re.compile("[a-zA-Z0-9]*EN-[a-zA-Z0-9]*"), name)):
                    color_choice = colors[3]
                    ymin, xmax = .02, 500
                    name = name.replace('EN-', ' ENCODE-')
                elif (re.match(re.compile("[a-zA-Z0-9]*Liu"), name)):
                    color_choice = colors[4]
                    name = name.replace('Liu', ' Liu')
                    ymin, xmax = .02, 1000
                elif (re.match(re.compile("[a-zA-Z0-9]*TRRUST"), name)):
                    color_choice = colors[5]
                    name = name.replace('TRRUST', ' TRRUST')
                    ymin, xmax = .02, 500
                elif (re.match(re.compile("[a-zA-Z0-9]*Mi"), name)):
                    color_choice = colors[6]
                    name = name.replace('Mi', ' miRT')
                    ymin, xmax = .02, 210
                else:
                    color_choice = colors[7]


            sim_net = nx.read_edgelist(sim_net_file, nodetype=int, create_using=nx.DiGraph())
            real_net = custom_load(network_file.strip())
            real_alpha = .4
            #if (len(real_nodes) != len(sim_nodes)): print("WARNING: real net does not have same number of nodes as simulation.")
            #if (len(real_net.edges()) != len(sim_net.edges())): print("WARNING: real net does not have same number of edges as simulation.")

            real_degrees, real_in_degrees, real_out_degrees = list(real_net.degree().values()),  list(real_net.in_degree().values()), list(real_net.out_degree().values())
            sim_degrees, sim_in_degrees, sim_out_degrees = list(sim_net.degree().values()),  list(sim_net.in_degree().values()), list(sim_net.out_degree().values())

            direction = 'both'
            H = []

            # PLOT REAL NET
            title = plot_title + "_" + str(name)

            real_deg, sim_deg = None, None
            if (direction == 'in'): real_deg, sim_deg = real_in_degrees, sim_in_degrees
            elif (direction == 'out'): real_deg, sim_deg = real_out_degrees, sim_out_degrees
            elif (direction == 'both'): real_deg, sim_deg = real_degrees, sim_degrees

            degs, freqs = np.unique(real_deg, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f / tot) * 100 for f in freqs]
            #plt.scatter(degs, freqs, color=color_choice, alpha=real_alpha)
            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=1, color=color_choice, alpha=real_alpha, markersize=10, marker='|', markeredgecolor=color_choice, mew=5)
            # you can also scatter the in/out degrees on the same plot
            # plt.scatter( .... )
            patch = mpatches.Patch(color=color_choice, label=name)
            H = H + [patch]

            # PLOT SIM NET

            degs, freqs = np.unique(sim_deg, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f / tot) * 100 for f in freqs]
            #plt.scatter(degs, freqs, color='#000000', alpha=1)
            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=1, color='#000000', alpha=1, markersize=10, marker='_', markeredgecolor='#000000', mew=5)

            patch = mpatches.Patch(color='#000000', label="Simulation")
            H = H + [patch]

            # FORMAT PLOT
            matplotlib.rcParams.update({'font.size': 14})
            ax = plt.gca()  # gca = get current axes instance

            # ax.set_xscale('log') #for scatter i think
            # ax.set_yscale('log')
            #ax.set_xlim([0.7, 200]) #TODO: change these?
            #ax.set_ylim([.1, 100])
            ax.set_xlim([.5,xmax])
            ax.set_ylim([ymin,100])

            xfmatter = ticker.FuncFormatter(LogXformatter)
            yfmatter = ticker.FuncFormatter(LogYformatter)
            ax.get_xaxis().set_major_formatter(xfmatter)
            ax.get_yaxis().set_major_formatter(yfmatter)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tick_params(axis='both', which='both', right='off', top='off')  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
            plt.legend(loc='upper right', handles=H, frameon=False, fontsize=11)
            plt.xlabel('degree  ', fontsize=20)
            plt.ylabel('% nodes ', fontsize=20)
            # plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

            plt.tight_layout()
            plt.savefig(str(title) + ".png", dpi=300,bbox='tight')  # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
            plt.clf()
            plt.cla()
            plt.close()

            i += 1


def plot_em(real_net_file, sim_net_file, plot_title):
    input_files = open(real_net_file,'r').readlines()

    colors = ['#ADECD7', '#ADC0F3','#E4B2FB','#FBB2B2','#FFCC66','#C3F708']
    i = 0
    for  line in input_files:
        H = []
        sim_net = nx.read_edgelist(sim_net_file, nodetype=int, create_using=nx.DiGraph())
        num_nodes = len(sim_net.nodes())

        # PLOT REAL NETS
        line         = line.strip()
        title        = line.split()[:-1][0]
        network_file = line.split()[-1]

        M = nx.read_gpickle(network_file)

        repeats = 100
        ENR = 0
        for j in range(repeats):
            sample_nodes = rd.sample(M.nodes(), num_nodes)
            ENR += len(M.edges(sample_nodes))/float(len(sample_nodes))
            degrees = list(M.degree(sample_nodes).values())

            #NP GET FREQS
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f/tot)*100 for f in freqs]

            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = colors[i], alpha=0.25, markersize=8, marker='.', markeredgecolor='None', )
            # can also plt.scatter( .... )


        #i think one patch per set of samples?
        patch =  mpatches.Patch(color=colors[i], label=title)
        ENR /= repeats

        H = H + [patch]

        #PLOT SIM NET
        degrees = list(sim_net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f / tot) * 100 for f in freqs]
        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=.5, color='#000000', alpha=1, markersize=10, marker='.', markeredgecolor='None')

        patch = mpatches.Patch(color='#000000', label="Simulation")

        H = H + [patch]

        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance
        #ax.set_xscale('log')
        #ax.set_yscale('log')
        ax.set_xlim([0.7,200])
        ax.set_ylim([.1,100])

        xfmatter = ticker.FuncFormatter(LogXformatter)
        yfmatter = ticker.FuncFormatter(LogYformatter)
        ax.get_xaxis().set_major_formatter(xfmatter)
        ax.get_yaxis().set_major_formatter(yfmatter)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
        plt.xlabel('degree  ')
        plt.ylabel('% genes ')
        #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

        plt.tight_layout()
        plt.savefig(str(plot_title) + " vs " + str(title) + ".png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
        plt.clf()
        plt.cla()
        plt.close()

        i += 1

def walklevel(some_dir, level=1): #MOD to dirs only
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield dirs
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]



###################################################
def LogYformatter(y, _):
    if int(y) == float(y) and float(y)>0:
        return str(int(y))+' %'
    elif float(y) >= .1:
        return str(y)+' %'
    else:
        return ""
###################################################
def LogXformatter(x, _):
    if x<=1:
        return str(int(x))
    if math.log10(x)  == int(math.log10(x)):
        return str(int(x))
    else:
        return ""
##################################################################
def update_rcParams():
    font_path = '/home/2014/choppe1/Documents/EvoNet/virt_workspace/fonts/adobe/Adobe_Caslon_Pro_Regular.ttf'
    prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = prop.get_name()
    rcParams['font.serif']         = 'Helvetica' #['Bitstream Vera Sans', 'DejaVu Sans', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']

    rcParams['axes.labelsize'] = 16
    rcParams['axes.titlesize'] = 20
    rcParams['grid.alpha'] = 0.1
    rcParams['axes.grid']=False
    rcParams['savefig.pad_inches']=.001
    rcParams['grid.color']='grey'

    rcParams['xtick.color']        =  'black'    #  ax.tick_params(axis='x', colors='red'). This will set both the tick and ticklabel to this color. To change labels' color, use: for t in ax.xaxis.get_ticklabels(): t.set_color('red')
    rcParams['xtick.direction']    =  'out'      # ax.get_yaxis().set_tick_params(which='both', direction='out')
    rcParams['xtick.labelsize']    =  12
    rcParams['xtick.major.pad']    =  1.0
    rcParams['xtick.major.size']   =  6     # how long the tick is
    rcParams['xtick.major.width']  =  1
    rcParams['xtick.minor.pad']    =  1.0
    rcParams['xtick.minor.size']   =  2.5
    rcParams['xtick.minor.width']  =  0.5
    rcParams['xtick.minor.visible']=  False


    rcParams['ytick.color']        =  'black'       # ax.tick_params(axis='x', colors='red')
    rcParams['ytick.direction']    =  'out'         # ax.get_xaxis().set_tick_params(which='both', direction='out')
    rcParams['ytick.labelsize']    =  12
    rcParams['ytick.major.pad']    =  2
    rcParams['ytick.major.size']   =  6
    rcParams['ytick.major.width']  =  1
    rcParams['ytick.minor.pad']    =  2.0
    rcParams['ytick.minor.size']   =  2.5
    rcParams['ytick.minor.width']  =  0.5
    rcParams['ytick.minor.visible']=  False
    return prop
##################################################################

def custom_load(net_path):
    edges_file = open (net_path,'r') #note: with nx.Graph (undirected), there are 2951  edges, with nx.DiGraph (directed), there are 3272 edges
    M=nx.DiGraph()     
    next(edges_file) #ignore the first line
    for e in edges_file: 
        interaction = e.split()
        assert len(interaction)>=2
        source, target = str(interaction[0]).strip().replace("'",'').replace('(','').replace(')',''), str(interaction[1]).strip().replace("'",'').replace('(','').replace(')','')
        if (len(interaction) >2):
            if (str(interaction[2]) == '+'):
                Ijk=1
            elif  (str(interaction[2]) == '-'):
                Ijk=-1
            else:
                print ("Error: bad interaction sign in file "+str(edges_file)+"\nExiting...")
                sys.exit()
        else:
            Ijk=util.flip()     
        M.add_edge(source, target, sign=Ijk)    
    return M


def plot_dir(parent_dir, pairs):
    #path is specific to rupert/yamaska servers
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_nets.txt"
    print("plotting " + str(len(pairs)) + " dirs for comparison with real networks.")

    for pair in pairs:
        sim, real_name = pair.split(':')
        print("Plotting sim dir " + str(sim) + " vs real " + str(real_name))
        sim_dirr = str(base_dir + parent_dir + sim)

        if not os.path.exists(sim_dirr + "/comparison_plots/"):
            os.makedirs(sim_dirr + "/comparison_plots/")
        for sim_file in os.listdir(sim_dirr+"/nets/"):
            print("Plotting sim file " + str(sim_file))
            plot_pairs(real_net_file, real_name, sim_dirr +"/nets/"+ sim_file, sim_dirr + "/comparison_plots/" + sim_file)


if __name__ == "__main__":

    parent_dir = sys.argv[1]
    pairs = sys.argv[2:]

    plot_dir(parent_dir, pairs)

    print("\nDone.\n")
