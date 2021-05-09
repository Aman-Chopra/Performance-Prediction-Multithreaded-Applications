# Steps to create the dataset:

# Download and build parsec benchmark
# wget http://parsec.cs.princeton.edu/download/3.0/parsec-3.0.tar.gz
# tar -xzf parsec-3.0.tar.gz
# source env.sh

# lscpu: Machine configurations:

# Architecture:          x86_64
# CPU op-mode(s):        32-bit, 64-bit
# Byte Order:            Little Endian
# CPU(s):                64
# On-line CPU(s) list:   0-63
# Thread(s) per core:    2
# Core(s) per socket:    8
# Socket(s):             4
# NUMA node(s):          8
# Vendor ID:             AuthenticAMD
# CPU family:            21
# Model:                 1
# Model name:            AMD Opteron(TM) Processor 6272
# Stepping:              2
# CPU MHz:               2099.972
# BogoMIPS:              4199.94
# Virtualization:        AMD-V
# L1d cache:             16K
# L1i cache:             64K
# L2 cache:              2048K
# L3 cache:              6144K
# NUMA node0 CPU(s):     0-7
# NUMA node1 CPU(s):     8-15
# NUMA node2 CPU(s):     32-39
# NUMA node3 CPU(s):     40-47
# NUMA node4 CPU(s):     48-55
# NUMA node5 CPU(s):     56-63
# NUMA node6 CPU(s):     16-23
# NUMA node7 CPU(s):     24-31

# Importing modules
import subprocess, sys, os

# Extracting the real execution time of a parsec program from stdout
def get_real_time(cmd_output):
    for line in iter(cmd_output,''):
        if line.__contains__('real'):
            line = line.split("\t")
            real_time = line[1]
            m,s = real_time.split('m')
            s,seconds = s.split('s')
            real_time = int(m) * 60 + float(s)
            break
    return real_time

def construct(pkg_name): 
    package_name = pkg_name
    number_of_threads = [1,2,4,8]
    input_size = ['simsmall','simmedium','simlarge']
    outputstream = open("dataset.csv", "a") 

    # Problem_name, number_of_threads, size, events, execution_time, speed_up
    # events = branch-instructions, branch-miss-rate in %, L3-cache-misses, L3-cache_miss_rate in %, L3-cache-references, cpu-cycles, 
    # total instructions in user space, IPC, cpu-clock, page-faults, L1-data-cache-loads, L1-instruction-cache-load-misses, LLc(Last level cache)-load-misses
    for size in input_size:
        for thread in number_of_threads:
            cmd = subprocess.Popen('parsecmgmt -a run -p ' + package_name + ' -n ' + str(thread) + ' -i ' + size, shell=True, stdout=subprocess.PIPE)
            cmd.wait()
            real_time_seconds = get_real_time(cmd.stdout.readline)
            if(thread == 1):
                single_thread_time = real_time_seconds
            speed_up = single_thread_time/real_time_seconds
            outputstream.write(package_name + "," + str(thread) + "," + str(size) + ",")
            cmd = subprocess.Popen('perf stat -o output.txt --field-separator=, -e branch-instructions,branch-misses,cache-misses,cache-references,cycles,instructions,cpu-clock,page-faults,L1-dcache-loads,L1-icache-load-misses,LLC-load-misses -- parsecmgmt -a run -p ' + package_name + ' -n ' + str(thread) + ' -i ' + size, shell=True, stdout=subprocess.PIPE)
            cmd.wait()
            with open("output.txt", "r") as f:
                lines = f.readlines()
            for currentline in lines[2:]:
                values = currentline.split(",")
                event_value = values[0]
                event_name = values[2]
                if(event_name.startswith('instructions')):
                    IPC = values[5] # Extracting Instructions per second
                    outputstream.write(event_value + "," + IPC + ",")
                elif(event_name.startswith('cache-misses')):
                    cache_miss_rate = values[5] # Extracting Cache miss rate
                    outputstream.write(event_value + "," + cache_miss_rate + ",")
                elif(event_name.startswith('branch-misses')):
                    branch_miss_rate = values[5] # Extracting Branch miss rate
                    outputstream.write(branch_miss_rate + ",")
                else:
                    outputstream.write(event_value + ",")
            outputstream.write(str(real_time_seconds) + "," + str(speed_up) + "\n")

    outputstream.close()

def main():
    # Building, Running, and uninstalling one module at a time due to user space constraints in crunchy
    modules = ['blackscholes', 'bodytrack', 'canneal', 'facesim', 'ferret', 'fluidanimate', 'freqmine', 'streamcluster', 'swaptions', 'vips', 'x264']
    outputstream = open("data.csv", "a") 
    outputstream.write("Name, Threads, Size, branch-instructions, branch-misses in %, L3-cache-misses, L3-cache-miss-rate in %, L3-cache-references, cpu-cycles, total-instructions, IPC, cpu-clock, page-faults, L1-data-cache-loads, L1-instruction-cache-load-misses, LLC-load-misses, Exe-time, Speedup\n")
    outputstream.close()
    for module in modules:
        cmd = subprocess.Popen('parsecmgmt -a build -p ' + module, shell=True, stdout=subprocess.PIPE)
        cmd.wait()
        construct(module)
        cmd = subprocess.Popen('parsecmgmt -a fulluninstall -p ' + module, shell=True, stdout=subprocess.PIPE)
        cmd.wait()

if __name__ == "__main__":
    main()
