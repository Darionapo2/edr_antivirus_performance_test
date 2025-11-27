import os

from PerformanceTest import PerformanceTest
from multiprocess_run import run_concurrent_tests
from utils import *


def scenario_no_multithreading():
    performance_test = PerformanceTest(
        server_id=SERVER_ID,
        instance_id=INSTANCE_ID
    )

    performance_test.reset(input_files_dir='files')

    # performance_test.run_sequentially(iterations=2)


def concurrent_instances():
    config = [
        {'server_id': SERVER_ID, 'instance_id': INSTANCE_ID},
        {'server_id': '127.0.0.1', 'instance_id': 2},
        {'server_id': '127.0.0.1', 'instance_id': 3},
        {'server_id': '127.0.0.1', 'instance_id': 4},
        {'server_id': '127.0.0.1', 'instance_id': 5},
        {'server_id': '127.0.0.1', 'instance_id': 6},
        {'server_id': '127.0.0.1', 'instance_id': 7},
        {'server_id': '127.0.0.1', 'instance_id': 8},
    ]

    run_concurrent_tests(config, n_instances=8, delay_s=0)

def concurrent_instances_debug():
    config = [
        {'server_id': SERVER_ID, 'instance_id': INSTANCE_ID}
    ]

    run_concurrent_tests(config, n_instances=1, delay_s=0)


def generate_report():
    pass


if __name__ == '__main__':
    concurrent_instances()

    generate_report()
