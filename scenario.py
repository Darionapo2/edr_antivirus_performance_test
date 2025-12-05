import subprocess
from datetime import datetime
import os
import time
from PerformanceTest import PerformanceTest
from multiprocess_run import run_concurrent_tests
from utils import *


def scenario_no_multithreading():
    performance_test = PerformanceTest(
        server_id=SERVER_ID,
        instance_id=INSTANCE_ID,
        run_id='run_debug'
    )

    performance_test.reset(input_files_dir='files')

    # performance_test.run_sequentially(iterations=2)


def concurrent_instances():

    run_id = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    run_dir_testdata = os.path.join('testdata', run_id)
    run_dir_logs = os.path.join('logs', run_id)
    os.makedirs(run_dir_testdata, exist_ok=True)
    os.makedirs(run_dir_logs, exist_ok=True)

    config = [
        {'server_id': SERVER_ID, 'instance_id': INSTANCE_ID, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 2, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 3, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 4, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 5, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 6, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 7, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': 'C:\\Users\\ZUXT2546_DA\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts\\pocnetapp (10.1.68.50)'},
        {'server_id': '127.0.0.1', 'instance_id': 8, 'run_id': run_id, 'unmonitored_dir': 'unmonitored', 'monitored_dir': '\\\\T14G4-PF4RA1BE\\performance_test_monitored'},
    ]

    run_concurrent_tests(config, n_instances=8, avg_time_s=3, min_perc=0.5, max_perc=0.5)

def concurrent_instances_debug():
    config = [
        {'server_id': SERVER_ID, 'instance_id': INSTANCE_ID}
    ]

    run_concurrent_tests(config, n_instances=1, avg_time_s=3, min_perc=0.5, max_perc=0.5)


if __name__ == '__main__':
    concurrent_instances()
