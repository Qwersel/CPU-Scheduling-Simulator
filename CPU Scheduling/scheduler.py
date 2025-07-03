import collections
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s')

class Scheduler:
    #Process manag
    def __init__(self):
        self.ready_queue = collections.deque()
        self.all_processes = []
        self.current_time = 0
        self.cpu_idle_time = 0
        self.current_running_process = None
        self.gantt_chart = [] # For storing things

        logging.info("Scheduler initialized.")

    def add_process(self, process):
        """Adds a new process to the system, sorted by arrival time."""
        self.all_processes.append(process)
        self.all_processes.sort(key=lambda p: p.arrival_time)
        logging.info(f"Process P{process.pid} added (Arrival: {process.arrival_time}, Burst: {process.burst_time}).")

    def _add_arriving_processes_to_ready_queue(self):
        """Moves arrived processes into the ready queue."""
        newly_arrived = []
        for p in self.all_processes:
            if (p.arrival_time <= self.current_time and
                p.remaining_burst_time > 0 and
                p not in self.ready_queue and
                p != self.current_running_process):
                newly_arrived.append(p)
        
        # PID sort syst
        newly_arrived.sort(key=lambda p: p.pid)

        for p in newly_arrived:
            self.ready_queue.append(p)

    def run_fcfs(self):
        #FCFS
        logging.info("Starting FCFS simulation.")
        self._reset_simulation_state()

        completed_count = 0
        total_processes = len(self.all_processes)

        while completed_count < total_processes:
            self._add_arriving_processes_to_ready_queue()

            if not self.current_running_process and self.ready_queue:
                self.current_running_process = self.ready_queue.popleft()
                if self.current_running_process.start_time is None:
                    self.current_running_process.start_time = self.current_time
                    self.current_running_process.response_time = self.current_time - self.current_running_process.arrival_time

            if self.current_running_process:
                start_time_slice = self.current_time
                self.current_running_process.remaining_burst_time -= 1
                self.current_time += 1
                end_time_slice = self.current_time

                self.gantt_chart.append((self.current_running_process.pid, start_time_slice, end_time_slice))

                if self.current_running_process.remaining_burst_time == 0:
                    self.current_running_process.completion_time = self.current_time
                    self.current_running_process.calculate_metrics()
                    logging.info(f"P{self.current_running_process.pid} completed at time {self.current_time}")
                    completed_count += 1
                    self.current_running_process = None
            else:
                self.cpu_idle_time += 1
                self.current_time += 1
                self.gantt_chart.append((0, self.current_time - 1, self.current_time)) # idle is 0

            self._advance_idle_time_to_next_arrival(completed_count, total_processes)

        logging.info("FCFS simulation finished.")
        self.display_results()

    def run_round_robin(self, time_quantum):
        #Round Robin
        logging.info(f"Starting Round Robin simulation with quantum = {time_quantum}.")
        self._reset_simulation_state()

        completed_count = 0
        total_processes = len(self.all_processes)

        while completed_count < total_processes:
            self._add_arriving_processes_to_ready_queue()

            if not self.current_running_process and self.ready_queue:
                self.current_running_process = self.ready_queue.popleft()
                if self.current_running_process.start_time is None:
                    self.current_running_process.start_time = self.current_time
                    self.current_running_process.response_time = self.current_time - self.current_running_process.arrival_time

            if self.current_running_process:
                execution_slice = min(self.current_running_process.remaining_burst_time, time_quantum)
                
                for _ in range(execution_slice):
                    self.current_running_process.remaining_burst_time -= 1
                    self.current_time += 1
                    self.gantt_chart.append((self.current_running_process.pid, self.current_time - 1, self.current_time))
                    self._add_arriving_processes_to_ready_queue() # Tests for arrivals every time unit

                if self.current_running_process.remaining_burst_time == 0:
                    self.current_running_process.completion_time = self.current_time
                    self.current_running_process.calculate_metrics()
                    logging.info(f"P{self.current_running_process.pid} completed at time {self.current_time}")
                    completed_count += 1
                    self.current_running_process = None
                else:
                    self.ready_queue.append(self.current_running_process)
                    self.current_running_process = None
            else:
                self.cpu_idle_time += 1
                self.current_time += 1
                self.gantt_chart.append((0, self.current_time - 1, self.current_time)) # 0 is for idle again

            self._advance_idle_time_to_next_arrival(completed_count, total_processes)

        logging.info("Round Robin simulation finished.")
        self.display_results()

    def _reset_simulation_state(self):
        """Resets scheduler and process states for a new simulation run."""
        self.current_time = 0
        self.cpu_idle_time = 0
        self.gantt_chart = []
        self.ready_queue.clear()
        self.current_running_process = None
        for p in self.all_processes:
            p.remaining_burst_time = p.burst_time
            p.start_time = None
            p.completion_time = None
            p.waiting_time = 0
            p.turnaround_time = 0
            p.response_time = None

    def _advance_idle_time_to_next_arrival(self, completed_count, total_count):
        """Advances time if CPU is idle and processes are yet to arrive."""
        if not self.ready_queue and self.current_running_process is None and completed_count < total_count:
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

    def display_results(self):
        """Displays the Gantt chart and performance metrics."""
        print("\n--- Simulation Results ---")
        print(f"Total Simulation Time: {self.current_time} units")
        print(f"CPU Idle Time: {self.cpu_idle_time} units")
        
        cpu_utilization = ((self.current_time - self.cpu_idle_time) / self.current_time) * 100 if self.current_time > 0 else 0
        print(f"CPU Utilization: {cpu_utilization:.2f}%")

        print("\n--- Gantt Chart ---")
        gantt_str = ""
        last_end_time = 0
        for pid, start, end in self.gantt_chart:
            if start > last_end_time: # Here we handle gaps
                gantt_str += f"| Idle ({start - last_end_time}u) "
            
            if pid == 0: # Marking idle time
                gantt_str += f"| Idle ({end - start}u) "
            else:
                gantt_str += f"| P{pid} ({end - start}u) "
            last_end_time = end
        
        gantt_str += "|"
        print(gantt_str)

        print("\n \ Final Metrics /")
        print(f"{'PID':<5}{'Arrival':<10}{'Burst':<10}{'Start':<10}{'Completion':<12}{'Turnaround':<12}{'Waiting':<10}{'Response':<10}")
        print("-" * 80)
        
        total_turnaround_time = 0
        total_waiting_time = 0
        total_response_time = 0
        num_completed_processes = 0

        sorted_processes = sorted(self.all_processes, key=lambda p: p.pid)

        for p in sorted_processes:
            if p.completion_time is not None:
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
            print(f"\nAverage Turnaround: {avg_turnaround_time:.2f}")
            print(f"Average Waiting: {avg_waiting_time:.2f}")
            print(f"Average Response: {avg_response_time:.2f}")
        else:
            print("\nNo processes = no calculations. Try 'reset' for better luck next time")
        
        print("---------------------------\n")

