import sys,os,subprocess,time
#sys.path.insert(0, os.getenv('lib'))

size, input_file = None,None
try:
    size, input_file = int(sys.argv[1].strip()), sys.argv[2]
    assert os.path.isfile(input_file)
except:
    print ("\nUsage: python ROOT.py [number_of_processors] [/path/to/input/file.txt (containing paths to configs files)]\nExiting ..")
    sys.exit(1)

CONFIG_FILES = [line.strip() for line in (open(input_file,'r')).readlines() if len(line.strip())>0] #line.strip()[0] != '#' and
i=0
for config_file in CONFIG_FILES:
    i+=1
    sys.stdout.write (str(i)+'/'+str(len(CONFIG_FILES))+": "+config_file+'\n')
    sys.stdout.flush()
    if  config_file.strip()[0]=='#':
        sys.stdout.write (' ... PREVIOUSLY DONE '+time.strftime("%B-%d-%Y-h%Hm%Ms%S")+'\n')
        sys.stdout.flush()
        continue
    # mpirun --mca mpi_warn_on_fork 0 -n 32 python3 $SIMULATION_SCRIPTv4 $SIMULATION_CONFIGSv4
    sim_script = os.getenv('SIMULATION_SCRIPT')
    #sim_script = '/home/chopper/src/evolve_root.py' #TODO: check this, but i think it is no longer needed
    cmd      = ['mpirun','--mca','mpi_warn_on_fork','0','-n',str(size),'python3', sim_script, config_file]
    if 'mpl' in sim_script.split('/')[-1]:
        cmd = ['python3', sim_script, config_file]
    success  = (subprocess.Popen (cmd, stdout=subprocess.PIPE, universal_newlines=True)).stdout.read()
    if success:
        CONFIG_FILES[i-1] = '# [DONE] '+config_file
        with open (input_file,'w') as f:
            f.write('\n'.join(CONFIG_FILES))
        sys.stdout.write (' ... SUCCESS '+time.strftime("%B-%d-%Y-h%Hm%Ms%S")+'\n')
        sys.stdout.flush()
    else:
        sys.stdout.write (' ... FAILURE '+time.strftime("%B-%d-%Y-h%Hm%Ms%S")+'\n')
        sys.stdout.flush()

sys.stdout.write ("\n\nDONE ..\n")
sys.stdout.flush()
