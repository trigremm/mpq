__VERSION__ = "0.1.4"

import argparse
import time
import multiprocessing
import os
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--dir", default=".", required=False)
parser.add_argument("--run", action="store_true")
args = parser.parse_args()
DIR = args.dir
MODE = args.run
PROCESSES = multiprocessing.cpu_count() // 4
DRAFT = os.path.join(DIR, "draft.out")


def load_list():
    job_list = [
        os.path.join(DIR, i) for i in os.listdir(DIR)
        if i.endswith(".sh")
    ]
    job_list = sorted(job_list)
    return job_list


def sh(file):
    return f"bash {file}"


def pipeline(file):
    cmd = sh(file)
    with open (DRAFT, "a") as f:
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


def main():
    empty_task_queue = multiprocessing.Queue()
    full_task_queue = add_tasks(empty_task_queue)
    processes = []
    print(f"Running with {PROCESSES} processes!")
    start = time.time()
    for n in range(PROCESSES):
        p = multiprocessing.Process(
            target=process_tasks, args=(full_task_queue,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    print(f"Time taken = {time.time() - start:.10f}")


if __name__ == "__main__":
    main()
