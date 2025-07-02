import collections
import logging

# Configure logging for the Scheduler
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s')

class Scheduler:
    """
    Simulates a CPU scheduler, managing processes in a ready queue
    and executing them using FCFS or Round Robin algorithms.
    """
    def __init__(self):
        """
        Initializes the scheduler.
        """
        self.ready_queue = collections.deque()  # Processes waiting for CPU
        self.all_processes = []  # All processes added to the system
        self.current_time = 0  # Simulation time
        self.cpu_idle_time = 0 # Time CPU spends idle
        self.current_running_process = None
        self.gantt_chart = [] # To visualize execution: [(process_id, start_time, end_time)]

        logging.info("Scheduler initialized.")

    def add_process(self, process):
        """
        Adds a new process to the system. Processes are initially added to a list
        and will enter the ready queue when their arrival time is met.
        """
        self.all_processes.append(process)
        # Sort processes by arrival time to easily manage arrivals during simulation
        self.all_processes.sort(key=lambda p: p.arrival_time)
        logging.info(f"Process P{process.pid} added to system (Arrival: {process.arrival_time}, Burst: {process.burst_time}).")

    def _add_arriving_processes_to_ready_queue(self):
        """
        Moves processes from all_processes to ready_queue if their arrival_time
        is less than or equal to the current_time and they haven't been added yet.
        """
        # Use a temporary list to avoid modifying self.all_processes while iterating
        newly_arrived = []
        for p in self.all_processes:
            # Check if process has arrived AND is not yet in ready queue AND is not completed
            if p.arrival_time <= self.current_time and p.remaining_burst_time > 0 and p not in self.ready_queue and p != self.current_running_process:
                newly_arrived.append(p)
        
        # Sort newly arrived processes by PID to ensure consistent order for FCFS if they arrive at same time
        newly_arrived.sort(key=lambda p: p.pid)

        for p in newly_arrived:
            self.ready_queue.append(p)
            logging.debug(f"Time {self.current_time}: P{p.pid} arrived and added to ready queue.")
            # Remove from all_processes if it's purely for arrival management
            # For simplicity, we'll keep it in all_processes and just check if it's already in queue
            # or running to avoid re-adding.

    def run_fcfs(self):
        """
        Executes processes using the First-Come, First-Served (FCFS) scheduling algorithm.
        """
        logging.info("Starting FCFS simulation.")
        self.current_time = 0
        self.cpu_idle_time = 0
        self.gantt_chart = []
        self.ready_queue = collections.deque() # Clear queue for new simulation run
        
        # Reset processes for a fresh simulation run
        for p in self.all_processes:
            p.remaining_burst_time = p.burst_time
            p.start_time = None
            p.completion_time = None
            p.waiting_time = 0
            p.turnaround_time = 0
            p.response_time = None

        completed_processes_count = 0
        total_processes = len(self.all_processes)

        # Loop until all processes are completed
        while completed_processes_count < total_processes:
            self._add_arriving_processes_to_ready_queue()

            if self.current_running_process is None and self.ready_queue:
                # CPU is idle but ready queue has processes, pick next
                self.current_running_process = self.ready_queue.popleft()
                logging.debug(f"Time {self.current_time}: P{self.current_running_process.pid} selected for execution.")
                
                if self.current_running_process.start_time is None:
                    self.current_running_process.start_time = self.current_time
                    self.current_running_process.response_time = self.current_running_process.start_time - self.current_running_process.arrival_time

            if self.current_running_process:
                # Execute the current process for one time unit
                start_exec_time = self.current_time
                self.current_running_process.remaining_burst_time -= 1
                self.current_time += 1
                end_exec_time = self.current_time

                self.gantt_chart.append((self.current_running_process.pid, start_exec_time, end_exec_time))
                logging.debug(f"Time {start_exec_time}-{end_exec_time}: P{self.current_running_process.pid} running. Rem: {self.current_running_process.remaining_burst_time}")

                if self.current_running_process.remaining_burst_time == 0:
                    # Process completed
                    self.current_running_process.completion_time = self.current_time
                    self.current_running_process.calculate_metrics()
                    logging.info(f"Time {self.current_time}: P{self.current_running_process.pid} completed.")
                    completed_processes_count += 1
                    self.current_running_process = None # CPU becomes free
            else:
                # CPU is idle, no processes in ready queue or arrived yet
                self.cpu_idle_time += 1
                self.current_time += 1
                self.gantt_chart.append((0, self.current_time - 1, self.current_time)) # 0 for idle
                logging.debug(f"Time {self.current_time - 1}-{self.current_time}: CPU idle.")
            
            # Ensure all processes that have arrived are added to the ready queue before next iteration
            self._add_arriving_processes_to_ready_queue()

        logging.info("FCFS simulation finished.")
        self.display_results()

    def run_round_robin(self, time_quantum):
        """
        Executes processes using the Round Robin (RR) scheduling algorithm.

        Args:
            time_quantum (int): The maximum time a process can run before preemption.
        """
        logging.info(f"Starting Round Robin simulation with quantum = {time_quantum}.")
        self.current_time = 0
        self.cpu_idle_time = 0
        self.gantt_chart = []
        self.ready_queue = collections.deque() # Clear queue for new simulation run
        
        # Reset processes for a fresh simulation run
        for p in self.all_processes:
            p.remaining_burst_time = p.burst_time
            p.start_time = None
            p.completion_time = None
            p.waiting_time = 0
            p.turnaround_time = 0
            p.response_time = None

        completed_processes_count = 0
        total_processes = len(self.all_processes)

        while completed_processes_count < total_processes:
            self._add_arriving_processes_to_ready_queue()

            if self.current_running_process is None and self.ready_queue:
                # CPU is idle, pick next process from ready queue
                self.current_running_process = self.ready_queue.popleft()
                logging.debug(f"Time {self.current_time}: P{self.current_running_process.pid} selected for execution (RR).")
                
                if self.current_running_process.start_time is None:
                    self.current_running_process.start_time = self.current_time
                    self.current_running_process.response_time = self.current_running_process.start_time - self.current_running_process.arrival_time
            
            if self.current_running_process:
                # Execute for time_quantum or until burst_time finishes
                execution_slice = min(self.current_running_process.remaining_burst_time, time_quantum)
                
                start_exec_time = self.current_time
                for _ in range(execution_slice):
                    self.current_running_process.remaining_burst_time -= 1
                    self.current_time += 1
                    self.gantt_chart.append((self.current_running_process.pid, self.current_time - 1, self.current_time))
                    self._add_arriving_processes_to_ready_queue() # Check for new arrivals at each time unit

                logging.debug(f"Time {start_exec_time}-{self.current_time}: P{self.current_running_process.pid} ran for {execution_slice} units. Rem: {self.current_running_process.remaining_burst_time}")

                if self.current_running_process.remaining_burst_time == 0:
                    # Process completed
                    self.current_running_process.completion_time = self.current_time
                    self.current_running_process.calculate_metrics()
                    logging.info(f"Time {self.current_time}: P{self.current_running_process.pid} completed.")
                    completed_processes_count += 1
                    self.current_running_process = None # CPU becomes free
                else:
                    # Process not completed, put back in ready queue
                    self.ready_queue.append(self.current_running_process)
                    logging.debug(f"Time {self.current_time}: P{self.current_running_process.pid} preempted, added back to queue.")
                    self.current_running_process = None # CPU becomes free, will pick next from queue

            else:
                # CPU is idle, no processes in ready queue or arrived yet
                self.cpu_idle_time += 1
                self.current_time += 1
                self.gantt_chart.append((0, self.current_time - 1, self.current_time)) # 0 for idle
                logging.debug(f"Time {self.current_time - 1}-{self.current_time}: CPU idle.")
            
            # If all processes are done, but there was a final idle time, ensure loop terminates
            if not self.ready_queue and self.current_running_process is None and completed_processes_count == total_processes:
                break
            
            # If no processes are in the ready queue and none are running,
            # but there are still unarrived processes, advance time until next arrival.
            if not self.ready_queue and self.current_running_process is None and completed_processes_count < total_processes:
                next_arrival_time = float('inf')
                for p in self.all_processes:
                    if p.remaining_burst_time > 0 and p.arrival_time > self.current_time:
                        next_arrival_time = min(next_arrival_time, p.arrival_time)
                
                if next_arrival_time != float('inf'):
                    idle_duration = next_arrival_time - self.current_time
                    for _ in range(idle_duration):
                        self.cpu_idle_time += 1
                        self.current_time += 1
                        self.gantt_chart.append((0, self.current_time - 1, self.current_time))
                        logging.debug(f"Time {self.current_time - 1}-{self.current_time}: CPU idle (waiting for next arrival).")
                else:
                    # No more processes to arrive, and queue is empty, so we must be done.
                    break

        logging.info("Round Robin simulation finished.")
        self.display_results()


    def display_results(self):
        """
        Displays the Gantt chart and performance metrics.
        """
        print("\n--- Simulation Results ---")
        print(f"Total Simulation Time: {self.current_time} units")
        print(f"CPU Idle Time: {self.cpu_idle_time} units")
        
        cpu_utilization = ((self.current_time - self.cpu_idle_time) / self.current_time) * 100 if self.current_time > 0 else 0
        print(f"CPU Utilization: {cpu_utilization:.2f}%")

        print("\n--- Gantt Chart ---")
        # Format Gantt chart for better readability
        gantt_str = ""
        last_end_time = 0
        for pid, start, end in self.gantt_chart:
            if start > last_end_time: # Handle gaps (idle time not explicitly marked as PID 0)
                gantt_str += f"| Idle ({start - last_end_time}u) "
            
            if pid == 0: # Explicitly marked idle time
                 gantt_str += f"| Idle ({end - start}u) "
            else:
                gantt_str += f"| P{pid} ({end - start}u) "
            last_end_time = end
        
        gantt_str += "|"
        print(gantt_str)

        print("\n--- Process Metrics ---")
        print(f"{'PID':<5}{'Arrival':<10}{'Burst':<10}{'Start':<10}{'Completion':<12}{'Turnaround':<12}{'Waiting':<10}{'Response':<10}")
        print("-" * 80)
        
        total_turnaround_time = 0
        total_waiting_time = 0
        total_response_time = 0
        num_completed_processes = 0

        # Sort processes by PID for consistent output
        sorted_processes = sorted(self.all_processes, key=lambda p: p.pid)

        for p in sorted_processes:
            if p.completion_time is not None: # Only show metrics for completed processes
                total_turnaround_time += p.turnaround_time
                total_waiting_time += p.waiting_time
                total_response_time += p.response_time if p.response_time is not None else 0
                num_completed_processes += 1
                print(f"{p.pid:<5}{p.arrival_time:<10}{p.burst_time:<10}{p.start_time:<10}{p.completion_time:<12}{p.turnaround_time:<12}{p.waiting_time:<10}{p.response_time:<10}")
            else:
                print(f"{p.pid:<5}{p.arrival_time:<10}{p.burst_time:<10}{'-':<10}{'-':<12}{'-':<12}{'-':<10}{'-':<10} (Not Completed)")

        if num_completed_processes > 0:
            avg_turnaround_time = total_turnaround_time / num_completed_processes
            avg_waiting_time = total_waiting_time / num_completed_processes
            avg_response_time = total_response_time / num_completed_processes
            print(f"\nAverage Turnaround Time: {avg_turnaround_time:.2f}")
            print(f"Average Waiting Time: {avg_waiting_time:.2f}")
            print(f"Average Response Time: {avg_response_time:.2f}")
        else:
            print("\nNo processes completed to calculate averages.")
        
        print("---------------------------\n")

