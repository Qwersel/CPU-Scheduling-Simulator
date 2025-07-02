import logging
from process import Process
from scheduler import Scheduler

# Configure logging for the main CLI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLI - %(levelname)s - %(message)s')

def run_cli():
    """
    Runs the command-line interface for the CPU Scheduling simulation.
    """
    print("--- OS CPU Scheduling Simulator ---")
    print("Welcome! Add processes and run simulations.")

    scheduler = Scheduler()
    current_strategy = None
    time_quantum = None # Only relevant for Round Robin

    print("\n--- Commands ---")
    print("  add <arrival_time> <burst_time> - Add a new process (e.g., add 0 10)")
    print("  run fcfs                      - Run simulation using First-Come, First-Served")
    print("  run rr <quantum>              - Run simulation using Round Robin (e.g., run rr 2)")
    print("  list                          - List all added processes")
    print("  reset                         - Clear all processes")
    print("  quit                          - Exit the simulator")
    print("------------------\n")

    while True:
        try:
            command_line = input(f"Scheduler > ").strip().lower()
            parts = command_line.split()
            command = parts[0] if parts else ''

            if command == 'quit':
                print("Exiting simulator. Goodbye!")
                break
            elif command == 'add':
                if len(parts) == 3:
                    try:
                        arrival = int(parts[1])
                        burst = int(parts[2])
                        if arrival < 0 or burst <= 0:
                            print("Arrival time cannot be negative. Burst time must be positive.")
                            continue
                        new_process = Process(arrival, burst)
                        scheduler.add_process(new_process)
                        print(f"Added {new_process}")
                    except ValueError:
                        print("Invalid input. Arrival and burst times must be integers.")
                else:
                    print("Usage: add <arrival_time> <burst_time>")
            elif command == 'run':
                if len(parts) >= 2:
                    strategy = parts[1].lower()
                    if strategy == 'fcfs':
                        if len(parts) == 2:
                            current_strategy = 'fcfs'
                            scheduler.run_fcfs()
                        else:
                            print("Usage: run fcfs")
                    elif strategy == 'rr':
                        if len(parts) == 3:
                            try:
                                quantum = int(parts[2])
                                if quantum <= 0:
                                    print("Time quantum must be a positive integer.")
                                    continue
                                current_strategy = 'rr'
                                time_quantum = quantum
                                scheduler.run_round_robin(time_quantum)
                            except ValueError:
                                print("Invalid quantum. Please enter an integer.")
                        else:
                            print("Usage: run rr <quantum>")
                    else:
                        print("Invalid scheduling strategy. Choose 'fcfs' or 'rr'.")
                else:
                    print("Usage: run <strategy> [quantum_for_rr]")
            elif command == 'list':
                if not scheduler.all_processes:
                    print("No processes added yet.")
                else:
                    print("\n--- All Processes ---")
                    print(f"{'PID':<5}{'Arrival':<10}{'Burst':<10}")
                    print("-" * 25)
                    for p in sorted(scheduler.all_processes, key=lambda x: x.pid):
                        print(f"{p.pid:<5}{p.arrival_time:<10}{p.burst_time:<10}")
                    print("---------------------\n")
            elif command == 'reset':
                scheduler = Scheduler() # Reinitialize scheduler to clear all processes
                Process.next_pid = 1 # Reset PID counter
                print("All processes cleared. Scheduler reset.")
            else:
                print("Unknown command. Type 'help' for commands or refer to the list above.")

        except Exception as e:
            logging.error(f"An unexpected error occurred in CLI: {e}")
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_cli()

