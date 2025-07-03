import logging
import sys
from process import Process
from scheduler import Scheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_help():
    help_text = """
Commands:
  add <arrival> <burst>    New process
  run fcfs                 Run FCFS
  run rr <quantum>         Run Round Robin
  list                     List all processes
  reset                    Reset
  quit                     When you are done
"""
    print(help_text.strip())

def main():
    
    #its for the CPU Scheduling CLI tool.
    
    
    print("CPU Scheduling Simulator")



    print("Try ''help'' to see commands.\n")
#Now time for Scheduler
    scheduler = Scheduler() 

    while True:
        cmd = input("Scheduler> ").strip().lower()
        if not cmd:
            continue

        parts = cmd.split()
        command = parts[0]

        if command == 'quit':
            print("Chao!")
            sys.exit(0)

        elif command == 'help':
            print_help()

        elif command == 'add':
            if len(parts) != 3:
                print("add <arrival> <burst>")
                continue
            try:
                arrival, burst = int(parts[1]), int(parts[2])
                if arrival < 0 or burst <= 0:
                    print("Arrival must be >= 0 and burst > 0.")
                    continue
                p = Process(arrival, burst)
                scheduler.add_process(p)
                print(f"Added process PID {p.pid}")
            except ValueError:
                print("Arrival and burst time = integers.")

        elif command == 'run':
            if len(parts) < 2:
                print("run <fcfs|rr> [quantum]")
                continue
            strategy = parts[1]
            if strategy == 'fcfs':
                scheduler.run_fcfs()
            elif strategy == 'rr':
                if len(parts) != 3:
                    print("run rr <quantum>")
                    continue
                try:
                    quantum = int(parts[2])
                    scheduler.run_round_robin(quantum)
                except ValueError:
                    print("Quantum must be an integer, sorry it has be this way")
            else:
                print(f"Unknown strategy: {strategy}")

        elif command == 'list':
            if not scheduler.all_processes:
                print("no processes added")
                continue
            print(f"{'PID':<5}{'Arr':<6}{'Burst':<6}")
            for p in sorted(scheduler.all_processes, key=lambda x: x.pid):
                print(f"{p.pid:<5}{p.arrival_time:<6}{p.burst_time:<6}")

        elif command == 'reset':
            scheduler = Scheduler()
            Process.next_pid = 1
            print("You reset it yay! You may now use it again")

        else:
            print(f"Unknown command '{command}'. Try 'quit' if you don't understand how this works!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print("An unexpected error occurred. I must check logs for details...again")
