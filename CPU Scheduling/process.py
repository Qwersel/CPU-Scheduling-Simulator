class Process:
    next_pid = 1

    def __init__(self, arrival_time, burst_time):
        self.pid = Process.next_pid
        Process.next_pid += 1

        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst_time = burst_time

        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None

    def calculate_metrics(self):
        if self.completion_time is None or self.start_time is None:
            return

        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

    def __str__(self):
        return f"P{self.pid}(Arr={self.arrival_time}, Burst={self.burst_time}, Rem={self.remaining_burst_time})"
