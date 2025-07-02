class Process:
    """
    Represents a single process for CPU scheduling simulation.

    Attributes:
        pid (int): Unique Process ID.
        arrival_time (int): The time unit at which the process arrives in the system.
        burst_time (int): The total CPU time (in time units) required for the process to complete execution.
        remaining_burst_time (int): The remaining CPU time needed for execution.
                                    Initially set to burst_time.
        start_time (int or None): The time unit when the process first starts execution.
                                  None until it begins running.
        completion_time (int or None): The time unit when the process finishes execution.
                                       None until it completes.
        waiting_time (int): The total time the process spends waiting in the ready queue.
                            Calculated upon completion.
        turnaround_time (int): The total time from arrival to completion.
                               Calculated upon completion.
        response_time (int or None): The time from arrival until the first time it gets CPU.
                                     None until it starts running.
    """
    next_pid = 1  # Class-level variable to assign unique PIDs

    def __init__(self, arrival_time, burst_time):
        """
        Initializes a new Process instance.

        Args:
            arrival_time (int): The time unit the process arrives.
            burst_time (int): The total CPU time required.
        """
        self.pid = Process.next_pid
        Process.next_pid += 1  # Increment for the next process

        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst_time = burst_time

        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None # Time from arrival to first execution

    def calculate_metrics(self):
        """
        Calculates waiting time and turnaround time upon process completion.
        This should be called when the process transitions to 'TERMINATED'.
        Assumes completion_time and start_time are already set.
        """
        if self.completion_time is None or self.start_time is None:
            # Metrics can only be calculated if process has completed and started
            return

        self.turnaround_time = self.completion_time - self.arrival_time
        # Waiting time = Turnaround Time - Burst Time (total time spent in CPU)
        self.waiting_time = self.turnaround_time - self.burst_time
        
        # Response time is already set when it first starts execution
        # (self.response_time = self.start_time - self.arrival_time)

    def __lt__(self, other):
        """
        Defines less-than comparison for sorting processes, e.g., by arrival time.
        Useful for sorting processes in queues.
        """
        return self.arrival_time < other.arrival_time

    def __str__(self):
        """
        Returns a string representation of the Process for easy printing.
        """
        return (f"P{self.pid}(Arr={self.arrival_time}, Burst={self.burst_time}, "
                f"Rem={self.remaining_burst_time})")

