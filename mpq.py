__VERSION__ = '0.1.3'


import time
import multiprocessing
import os
import sys
import datetime

from secret import DIR # dir where scripts located

MODE = 'run' in sys.argv
PROCESSES = multiprocessing.cpu_count() // 2
DRAFT = os.path.join(DIR, 'draft.out')


def load_list():
    return [
        os.path.join(DIR, i) for i in os.listdir(DIR)
        if i.endswith('.sh')
    ]


def sh(file):
    return 'module load use.own; ' \
           'module load vcftools0113; ' \
           'module load python365; ' \
           f'bash {file}'


def pipeline(file):
    cmd = sh(file)
    with open (DRAFT, 'a') as f:
        f.write(f"{datetime.datetime.now():%Y%m%d_%H%M%S} {cmd}\n")
    if MODE: # if script is running with run option
        os.system(cmd)
    return


def process_tasks(task_queue):
    while not task_queue.empty():
        script = task_queue.get()
        pipeline(script)
    return True


def add_tasks(task_queue):
    for script in load_list():
        task_queue.put(script)
    return task_queue


def run():
    empty_task_queue = multiprocessing.Queue()
    full_task_queue = add_tasks(empty_task_queue)
    processes = []
    print(f'Running with {PROCESSES} processes!')
    start = time.time()
    for n in range(PROCESSES):
        p = multiprocessing.Process(
            target=process_tasks, args=(full_task_queue,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    print(f'Time taken = {time.time() - start:.10f}')


if __name__ == '__main__':
    run()
