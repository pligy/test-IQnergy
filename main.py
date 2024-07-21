from multiprocessing import Process, Queue, current_process
import time
from threading import Thread

class ProcessController:
    def __init__(self):
        self.max_proc = 1
        self.task_queue = Queue()
        self.active_processes = []
        self.max_exec_time = None
        self.manage_thread = None
        self.info_thread = None

    def set_max_proc(self, n):
        self.max_proc = n

    def start(self, tasks, max_exec_time):
        self.max_exec_time = max_exec_time
        for task in tasks:
            self.task_queue.put(task)

        if self.manage_thread is None or not self.manage_thread.is_alive():
            self.manage_thread = Thread(target=self._manage_tasks)
            self.manage_thread.start()
        if self.info_thread is None or not self.info_thread.is_alive():
            self.info_thread = Thread(target=self._print_info_periodically)
            self.info_thread.start()

    def _manage_tasks(self):
        while not self.task_queue.empty() or len(self.active_processes) > 0:
            self._start_tasks()
            self._cleanup_processes()
            time.sleep(0.1)

    def _start_tasks(self):
        while not self.task_queue.empty() and len(self.active_processes) < self.max_proc:
            func, args = self.task_queue.get()
            process = Process(target=self._run_task, args=(func, args, self.max_exec_time))
            process.start()
            self.active_processes.append(process)

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
        while not self.task_queue.empty() or any(p.is_alive() for p in self.active_processes):
            self._cleanup_processes()
            time.sleep(0.1)

        if self.info_thread is not None and self.info_thread.is_alive():
            self.info_thread.join()

    def wait_count(self):
        return self.task_queue.qsize()

    def alive_count(self):
        self._cleanup_processes()
        return len(self.active_processes)

    def _print_info_periodically(self):
        while not self.task_queue.empty() or any(p.is_alive() for p in self.active_processes):
            time.sleep(5)
            print(f"Tasks left in queue: {self.wait_count()}")
            print(f"Tasks currently running: {self.alive_count()}")


# Пример использования
def example_task(duration):
    print(f"Process {current_process().name} started, will run for {duration} seconds")
    time.sleep(duration)
    print(f"Process {current_process().name} finished")

if __name__ == "__main__":
    controller = ProcessController()
    controller.set_max_proc(6)

    tasks1 = [
        (example_task, (1,)),
        (example_task, (2,)),
        (example_task, (3,)),
        (example_task, (4,)),
        (example_task, (5,)),
        (example_task, (8,)),
        (example_task, (9,)),
    ]

    tasks2 = [
        (example_task, (2,)),
        (example_task, (10,)),
        (example_task, (11,))
    ]

    controller.start(tasks1, max_exec_time=15)
    controller.start(tasks2, max_exec_time=15)
    controller.start(tasks1, max_exec_time=15)
    controller.wait()

    print("All tasks are completed.")
