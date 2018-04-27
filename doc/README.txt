evoEvo is a project to evolve a population of networks to maximize the information conserved between nodes

note that some features have not been tested for awhile, these are marked by (!)
in less elegant cases, asserts may be used to ensure that certain parameter combos are not used (since not yet implemented)

example_configs.txt gives the currently ideal parameters (especially relevant for fitness parameters)

run.sh is specific to rupert/yamaska
rqmts.txt specifies the packages that need to be installed

PARAMETERS
# general
debug 				boolean; sequential run without mpi, often easier to debug
directed			boolean, directed or undirected graph
single_cc			boolean, maintain single connected component

# states
pressure			% of nodes or edges that are assigned a state
pressure_on			= nodes | edges; which objects states are applied to 
instance_states			experience | probabilistic, the later does not appear to work as well
state_distribution		probability distribution for states
sampling_rounds_multiplier	# instances = # nodes | edges * sampling_rounds_multiplier
sampling_rounds_max		caps # instances

# start and stop
initial_net_type        = random | load; load uses network_file parameter
		 	  other options available, but have not been used for awhile see init_nets.py
starting_size           = #nodes
stop_condition		= generation | size; determines which of the following configs are relevant
ending_size             = #nodes
max_generations         
edge_to_node_ratio      

network_file  		= full path to nx net, only relevant if initial_net_type = load

# population
number_of_workers       
num_worker_nets         
percent_survive         percent of total population used for next generation

# output
num_data_output     	comprised of degree distribution and several features
num_net_output        	full net is output, can be used for 'load'

# fitness
fitness_metric 		for undirected 'info' is the only option, see node_fitness.py for several attempts at directed metrics
fitness_direction       = max | min
scale_node_fitness      boolean; used for toying with addition normalization while calculating net fitness from node fitnesses 

# bias
biased                   boolean; bias the distribution of states
bias_on                  nodes | edges; does not need to be the same as pressure_on, although may make more sense if so
global_edge_bias         all objects have this same bias
bias_distribution        = uniform, normal, see bias.py for more; all objects have the same distribution (but may vary between one another)

# mutation				all mutations are per generation, if < 1 there is a probabilistic chance that they occur
add_edge_mutation_frequency     	(!)
remove_edge_mutation_frequency  	(!)
rewire_mutation_frequency       	(frequently used)
sign_mutation_frequency         	(!)
reverse_edge_mutation_frequency 	(!)
grow_mutation_frequency         	(!)
shrink_mutation_frequency       	(frequently used)

# partially implemented 		these remain in case future changes desire multiple simulations, possibly with the same advice (~ direct evolution)
num_sims	= 1			(!)
advice_creation	= each			(!)



OTHER DETAILS
- workers only execute 1 generation and have a static population size
