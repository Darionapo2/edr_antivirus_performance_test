import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from os.path import exists
from sys import implementation
import json

from PerformanceTest import PerformanceTest
from utils import *

def sleep_think_time(avg_time_s, min_perc, max_perc):
    if avg_time_s == 0:
        return 0

    min_s = avg_time_s * (1 - min_perc)

    if min_s < 0:
        min_s = 0

    max_s = avg_time_s * (1 + max_perc)

    if min_s > max_s:
        print('Error sleep_think_time: min_s > max_s')
        return 0

    time_s = random.uniform(min_s, max_s)
    time.sleep(time_s)
    return time_s

def run_concurrent_tests(config, n_instances=8, avg_time_s=0, min_perc=0, max_perc=0):

    # print out the number of physical CPUs available
    print(f'n. CPUs: {mp.cpu_count()}')

    result_files = []
    start_time = time.time()

    # ProcessPoolExecutor with immediate submit
    with ProcessPoolExecutor(max_workers=n_instances) as executor:

        futures = {}
        for i in range(n_instances):

            future = executor.submit(
                run_single_instance,
                **config[i]
            )

            futures[future] = i + 1
            print(f'Process {i + 1} started')

            sleep_think_time(avg_time_s, min_perc, max_perc)

        print('Waiting for all subprocesses to be done...')

        for future in as_completed(futures):
            instance_id = futures[future]
            print(f'Process {instance_id} completed')

            result_file = future.result()
            result_files.append(result_file)

    # Extracts run_id from config file passed to each instance.
    # It is assumed that run_dir is the same for each instance.
    run_id = config[0]['run_id']
    run_dir_testdata = os.path.join('testdata', run_id)

    # Merge all results into a single JSON
    merged_file = os.path.join(run_dir_testdata, 'merged_results.json')
    print(f'merged_file: {merged_file}')
    merge_json_files(result_files, merged_file)

    total_time = time.time() - start_time
    print('total time: ', total_time)


def run_single_instance(server_id, instance_id, run_id, monitored_dir=MONITORED_DIR, unmonitored_dir=UNMONITORED_DIR, random_resources=False):

    print('Instance Started')

    tester = PerformanceTest(
        server_id=server_id,
        instance_id=instance_id,
        run_id=run_id,
        monitored_dir=monitored_dir,
        unmonitored_dir=unmonitored_dir,
        random_resources=random_resources
    )

    tester.reset(input_files_dir='files')

    # Setup here the number of iterations
    operation_details = tester.run_sequentially(iterations=3)

    run_dir_testdata = os.path.join('testdata', run_id)

    out_file = os.path.join(
        run_dir_testdata,
        f"results_server{server_id}_instance{instance_id}_{time.time_ns()}.json"
    )

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(operation_details, f, ensure_ascii=False, indent=4)

    return out_file


def merge_json_files(json_files, output_file):

    merged = []
    for f in json_files:
        print(f)
        with open(f, 'r') as infile:
            merged.extend(json.load(infile))

    with open(output_file, 'w') as out:
        json.dump(merged, out, indent=4)
