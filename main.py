from multiprocessing import Process, Queue, current_process
import time

class ProcessController:
    def __init__(self):
        self.max_proc = 1
        self.task_queue = Queue()
        self.active_processes = []
        self.max_exec_time = None

    def set_max_proc(self, n):
        self.max_proc = n

    def start(self, tasks, max_exec_time):
        self.max_exec_time = max_exec_time
        for task in tasks:
            self.task_queue.put(task)
        self._start_tasks()

    def _start_tasks(self):
        while not self.task_queue.empty() and len(self.active_processes) < self.max_proc:
            func, args = self.task_queue.get()
            process = Process(target=self._run_task, args=(func, args, self.max_exec_time))
            process.start()
            self.active_processes.append(process)
            self._cleanup_processes()

    @staticmethod
    def _run_task(func, args, max_exec_time):
        p = Process(target=func, args=args)
        p.start()
        p.join(max_exec_time)
        if p.is_alive():
            p.terminate()
            p.join()

    def _cleanup_processes(self):
        self.active_processes = [p for p in self.active_processes if p.is_alive()]

    def wait(self):
        while any(p.is_alive() for p in self.active_processes):
            self._cleanup_processes()
            time.sleep(0.1)

    def wait_count(self):
        return self.task_queue.qsize()

    def alive_count(self):
        self._cleanup_processes()
        return len(self.active_processes)

# Пример использования
def example_task(duration):
    print(f"Process {current_process().name} started, will run for {duration} seconds")
    time.sleep(duration)
    print(f"Process {current_process().name} finished")

if __name__ == "__main__":
    controller = ProcessController()
    controller.set_max_proc(4)
    tasks = [
        (example_task, (7, )),
        (example_task, (3, )),
        (example_task, (1, )),
        (example_task, (2, )),
        (example_task, (4,))
    ]
    controller.start(tasks, max_exec_time=25)
    controller.wait()

    print("All tasks are completed.")
