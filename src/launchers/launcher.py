import os, sys, subprocess, time, socket
sys.path.insert(0, os.getenv('lib'))
import init, util
################################################################################################################################################
def compile_solvers(CONFIGS):
    solvers     = zip(CONFIGS['KP_solver_source'], CONFIGS['KP_solver_binary'])
    for KP_solver_source, KP_solver_binary in set(solvers):    
        soname = '-Wl,-soname,'+KP_solver_binary.split('/')[-1]
        compile = ['gcc', '-shared', soname, '-o', KP_solver_binary, '-fPIC', KP_solver_source]
        result = (subprocess.Popen (compile, stdout=subprocess.PIPE, universal_newlines=True)).stdout.read()       
        try:
            assert len(result) == 0
        except:
            return False
    return True
################################################################################################################################################
def set_qsub_outdir(CONFIGS):
    output_dirs = list(set(CONFIGS['output_directory']))
    qsub_output_dir = output_dirs[0]
    for dir in output_dirs[1:]:
        i=0
        qsub_output_dir = qsub_output_dir[0:min(len(dir), len(qsub_output_dir))]
        for i in range(len(qsub_output_dir)):
            if qsub_output_dir[i] != dir[i]:
                qsub_output_dir= qsub_output_dir[:i]
                break
    qsub_output_dir = util.slash(qsub_output_dir)
    if len(qsub_output_dir.split('/'))>2:
        qsub_output_dir = util.slash('/'.join(util.slash(qsub_output_dir).split('/')[:-1]))
    if not os.path.isdir(qsub_output_dir):
        try:
            os.makedirs(qsub_output_dir)
        except:
            print("Fatal: failed to creat dir "+qsub_output_dir+"\nExiting")
            log.write("Fatal: failed to creat dir "+qsub_output_dir+"\nExiting")
            sys.exit(1)

    return qsub_output_dir

################################################################################################################################################
def parseConfigs(input_file):
    config_files = [ os.path.realpath (path.replace('#','').replace('[DONE]','').strip()) for path in (open(input_file,'r')).readlines()]# if path[0]!='#']
    CONFIGS = {}
    for path in config_files:
        configs = [line.strip() for line in (open(path,'r')).readlines() if path[0]!='#' and '=' in line]
        for c in configs:
            c = c.split('=')
            try:
                k,v = c[0].strip(), c[1].strip()
            except:
                print(c)
                sys.exit(1)
            if k not in CONFIGS.keys():
                CONFIGS[k] = []
            CONFIGS[k].append(v)
    return CONFIGS
################################################################################################################################################
def launch(simulation_script, simulation_batch_root, launching_script, simulation_directory,launching_directory,input_file, qsub_simulation_arg, qsub_launching_arg, dependency_switch, log):
    os.environ['SIMULATION_SCRIPT']    = simulation_script
    os.environ['SIMULATION_BATCH_ROOT']= simulation_batch_root
    os.environ['LAUNCHING_SCRIPT']     = launching_script
    os.environ['SIMULATION_DIRECTORY'] = simulation_directory
    os.environ['LAUNCHING_DIRECTORY']  = launching_directory
    os.environ['SIMULATION_CONFIGS']   = input_file
    log.write("\nos.environ['SIMULATION_SCRIPT']   = "+os.getenv('SIMULATION_SCRIPT'))
    log.write("\nos.environ['SIMULATION_BATCH_ROOT']   = "+os.getenv('SIMULATION_BATCH_ROOT'))
    log.write("\nos.environ['LAUNCHING_SCRIPT']    = "+os.getenv('LAUNCHING_SCRIPT'))
    log.write("\nos.environ['SIMULATION_DIRECTORY']= "+os.getenv('SIMULATION_DIRECTORY'))
    log.write("\nos.environ['LAUNCHING_DIRECTORY'] = "+os.getenv('LAUNCHING_DIRECTORY'))
    log.write("\nos.environ['SIMULATION_CONFIGS']  = "+os.getenv('SIMULATION_CONFIGS'))
    log.write("\nPATH  = "+os.getenv('PATH'))
    log.write("\nLD_LIBRARY_PATH  = "+os.getenv('LD_LIBRARY_PATH'))
    print("os.environ['SIMULATION_CONFIGS']  = "+os.getenv('SIMULATION_CONFIGS'))
    print ("Please wait ..")    
    simulation_job_id   = (subprocess.Popen (qsub_simulation_arg, stdout=subprocess.PIPE, universal_newlines=True)).stdout.read().replace('\n','').strip()
    log.write ("\nSimulation job dispatched .. "+simulation_job_id+"\nI will wait 1 minute before dispatching the Launching job, Please wait ...")
    print(" ".join(qsub_simulation_arg))
    log.write ("\n\n"+" ".join(qsub_simulation_arg))
    print ("Simulation job dispatched ..: "+simulation_job_id+"\nI will wait 1 minute before dispatching the Launching job, Please wait ...")
    log.flush()
    time.sleep(60)
    launching_job_id    = (subprocess.Popen (qsub_launching_arg+[dependency_switch, "depend=afterany:"+simulation_job_id.split(".")[0]], stdout=subprocess.PIPE, universal_newlines=True)).stdout.read().replace('\n','').strip() 
    log.write ("\nLaunch job dispatched .. "+launching_job_id+"\n")  
    log.write ("\n\n"+" ".join(qsub_launching_arg+[dependency_switch, "depend=afterany:"+simulation_job_id.split(".")[0]]))
    print(" ".join(qsub_launching_arg+[dependency_switch, "depend=afterany:"+simulation_job_id.split(".")[0]]))
    print ("Launch job dispatched .. "+launching_job_id+"\n")
    log.flush()
    log.close()
################################################################################################################################################
def setup_qsub_command():
    launch_script=""
    sim_script= ""
    sub_cmd   = "qsub"
    dependency_switch ="-W"
    host = ''.join([i for i in socket.gethostname() if not i.isdigit()])
    if  "colosse" in host:
        print ("We are on colosse, eh!")
        sim_script = "simulation_job_colosse.sh"
        sub_cmd    = "msub"
        dependency_switch="-l"
        launch_script="launching_job_colosse.sh"
    elif "lg" in host or "gm" in host or "r-n" in host: #guililmin
        print ("We are on Guillimin, eh!")
        sim_script = "simulation_job_guillimin.sh"
        launch_script="launching_job_guillimin.sh"
    elif "ip" in host or "cp" in host: #mammoth
        print ("We are on Mammoth, eh!")
        sim_script = "simulation_job_mammoth.sh"
        launch_script="launching_job_mammoth.sh"
    else:
        print ("I couldn't determine which host is this: "+host)
        print ("Exiting ..")
        #sys.exit(1)
        pass
    return sim_script, launch_script, sub_cmd, dependency_switch, host
################################################################################################################################################
def setup ():
    timestamp   = time.strftime("%B-%d-%Y-h%Hm%Ms%S")
    
    log = open (os.path.join (util.slash(os.getenv('LAUNCHING_DIRECTORY')), "launcher_batch.log" ), "a") 
    if len(sys.argv) < 2 or not  (os.path.isfile (str(sys.argv[1])))  :
        log.write ("Usage: python3 launcher_vX.py [/absolute/path/to/input/file.txt (containing paths to configs files)]\nExiting..\n")
        sys.exit(1)  
    input_file   = str(sys.argv[1])
    job_name    =  input_file.split('/')[-1]
    job_name    = job_name[0:min(10,len(job_name))]
    
    return log, input_file, job_name, timestamp
################################################################################################################################################

if __name__ == "__main__":       
    log, input_file, job_name, timestamp = setup ()
    log.write("\n======================================\n"+time.strftime("%B-%d-%Y-h%Hm%Ms%S")+"\n======================================\n")
    configs = util.cleanPaths(input_file)
    if len(configs) == 0:
        log.write("\nlen(configs)==0; I will not start a new job. Goodbye\n")
        print ("\nlen(configs)==0; I will not start a new job. Goodbye\n")
        sys.exit(1)
    
    
    CONFIGS=parseConfigs(input_file)
    
    assert compile_solvers(CONFIGS)
    
    qsub_output_dir = set_qsub_outdir(CONFIGS)
    
    sim_script, launch_script, sub_cmd, dependency_switch, host = setup_qsub_command()
    
    qsub_simulation_arg         = [sub_cmd, "-N", job_name,  "-o",  qsub_output_dir+"qsub_simulation_output_"+host+'_'+job_name+'_'+timestamp+".txt", "-e",  qsub_output_dir+"qsub_simulation_error_"+host+'_'+job_name+'_'+timestamp+".txt", "-V", util.slash(os.getenv('LAUNCHING_DIRECTORY'))+sim_script]
    qsub_launching_arg          = [sub_cmd,  "-N", job_name,  "-o",  qsub_output_dir+"qsub_launching_output_"+host+'_'+job_name+'_'+timestamp+".txt", "-e",  qsub_output_dir+"qsub_launching_error_"+host+'_'+job_name+'_'+timestamp+".txt",  "-V", util.slash(os.getenv('LAUNCHING_DIRECTORY'))+launch_script]
    simulation_batch_root       = os.getenv('SIMULATION_BATCH_ROOT') 
    simulation_script           = os.getenv('SIMULATION_SCRIPT')
    launching_script            = os.getenv('LAUNCHING_SCRIPT') 
    simulation_directory        = os.getenv('SIMULATION_DIRECTORY') 
    launching_directory         = os.getenv('LAUNCHING_DIRECTORY')   
    

    launch (simulation_script, simulation_batch_root, launching_script,simulation_directory,launching_directory, input_file, qsub_simulation_arg, qsub_launching_arg, dependency_switch, log)
