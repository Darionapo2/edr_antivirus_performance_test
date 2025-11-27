import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from os.path import exists
from sys import implementation
import json

from PerformanceTest import PerformanceTest
from utils import *


def run_concurrent_tests(config, n_instances=8, delay_s=0):

    run_id = f"run_{int(time.time())}"
    run_dir = os.path.join("testdata", run_id)
    os.makedirs(run_dir, exist_ok=True)

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
                run_dir=run_dir,
                **config[i]
            )

            futures[future] = i + 1
            print(f'Process {i + 1} started')

            time.sleep(delay_s)

        print('Waiting for all subprocesses to be done...')

        for future in as_completed(futures):
            instance_id = futures[future]
            print('process', instance_id, 'completed')

            result_file = future.result()
            result_files.append(result_file)

    # Merge all results into a single JSON
    merged_file = os.path.join(run_dir, 'merged_results.json')
    merge_json_files(result_files, merged_file)

    total_time = time.time() - start_time
    print('total time: ', total_time)


def run_single_instance(server_id, instance_id, run_dir, monitored_dir=MONITORED_DIR, unmonitored_dir=UNMONITORED_DIR, random_resources=False):

    print('Instance Started')

    tester = PerformanceTest(
        server_id=server_id,
        instance_id=instance_id,
        monitored_dir=monitored_dir,
        unmonitored_dir=unmonitored_dir,
        random_resources=random_resources
    )

    tester.reset(input_files_dir='files')
    operation_details = tester.run_sequentially(iterations=2)

    out_file = os.path.join(
        run_dir,
        f"results_server{server_id}_instance{instance_id}_{time.time_ns()}.json"
    )

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(operation_details, f, ensure_ascii=False, indent=4)


def merge_json_files(json_files, output_file):

    merged = []
    for f in json_files:
        with open(f, 'r') as infile:
            merged.extend(json.load(infile))

    with open(output_file, 'w') as out:
        json.dump(merged, out, indent=4)
