import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from PerformanceTest import PerformanceTest
from utils import *


def run_concurrent_tests(config, n_instances=8, delay_s=0):

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

            time.sleep(delay_s)

        print('Waiting for all subprocesses to be done...')

        for future in as_completed(futures):

            instance_id = futures[future]

            print(instance_id, 'completed')

            result_file = future.result()
            result_files.append(result_file)

    total_time = time.time() - start_time
    print('total time: ', total_time)


def run_single_instance(server_id, instance_id, monitored_dir=MONITORED_DIR, unmonitored_dir=UNMONITORED_DIR, random_resources=False):

    print('Instance Started')

    tester = PerformanceTest(
        server_id=server_id,
        instance_id=instance_id,
        monitored_dir=monitored_dir,
        unmonitored_dir=unmonitored_dir,
        random_resources=random_resources
    )

    return tester.run()
