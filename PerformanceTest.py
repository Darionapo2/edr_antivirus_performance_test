import os
import queue
import random
import shutil
import socket
import logging
import string
import time
import uuid
from _datetime import datetime
import subprocess


class PerformanceTest:

    def __init__(self, server_id, instance_id, input_dir='input', output_dir='output', random_resources=True):
        self.server_id = server_id
        self.instance_id = instance_id
        self.random_resources = random_resources

        self.pid = os.getpid()
        self.hostname = socket.gethostname()
        self.unique_id = f'server{self.server_id}_instance{self.instance_id}'
        self._operation_counter = 0

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'server_id': self.server_id,
            'instance_id': self.instance_id,
            'unique_id': self.unique_id,
            'hostname': self.hostname,
            'pid': self.pid,
            'test_execution_order': [],
            'tests': []
        }

        self.operation_details = []

        # creating input and output dirs for each instance of PerformanceTest

        self.input_files_path = os.path.join(input_dir, 'files', self.unique_id)
        self.input_dirs_path = os.path.join(input_dir, 'dirs', self.unique_id)
        self.output_dirs_path = os.path.join(output_dir, 'dirs', self.unique_id)
        self.output_files_path = os.path.join(output_dir, 'files', self.unique_id)

        self.files_queue = []
        self.files_count = 0
        self.files_index = 0

        self.dirs_queue = []
        self.dirs_count = 0
        self.dirs_index = 0

        paths = [self.input_files_path, self.input_dirs_path, self.output_dirs_path, self.output_files_path]

        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

        self.collect_resources()

    def collect_resources(self):
        # collecting file objects
        files = [
            f for f in os.listdir(self.input_files_path)
            if os.path.isfile(
                os.path.join(self.input_files_path, f)
            )
        ]

        files = sorted(files)

        self.files_queue = files
        self.files_count = len(self.files_queue)

        # collecting dir objects

        dirs = [
            d for d in os.listdir(self.input_dirs_path)
            if os.path.isdir(
                os.path.join(self.input_dirs_path, d)
            )
        ]

        dirs = sorted(dirs)

        self.dirs_queue = dirs
        self.dirs_count = len(self.dirs_queue)

    def generate_unique_filename(self, prefix, extension):
        timestamp_ns = time.time_ns()
        unique_suffix = f'{timestamp_ns}_{self.pid}_{self._operation_counter:06d}_{uuid.uuid4().hex[:8]}'
        return f'{prefix}_{unique_suffix}{extension}'

    def generate_unique_folder_name(self, prefix):
        timestamp_ns = time.time_ns()
        unique_suffix = f'{timestamp_ns}_{self.pid}_{self._operation_counter:06d}_{uuid.uuid4().hex[:8]}'
        return f'{prefix}_{unique_suffix}'

    def measure_time(self, operation_func, op_details, *args, **kwargs):
        start_timestamp = datetime.now().isoformat()
        start_timestamp_ns = time.time_ns()
        start_time = time.perf_counter()

        try:
            result = operation_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.perf_counter()
        end_timestamp = datetime.now().isoformat()
        end_timestamp_ns = time.time_ns()
        elapsed_time = end_time - start_time

        detailed_record = {
            'operation_id': self._operation_counter,
            'operation_type': op_details['op_type'],
            'file_size': op_details['size'],
            'source_file_path': '',
            'file_path': op_details['path'],
            'start_timestamp': start_timestamp,
            'start_timestamp_ns': start_timestamp_ns,
            'end_timestamp': end_timestamp,
            'end_timestamp_ns': end_timestamp_ns,
            'duration_seconds': elapsed_time,
            'success': success,
            'error': error
        }

        self.operation_details.append(detailed_record)

        return elapsed_time, result, success, error

    def get_next_file(self):
        if self.random_resources:
            file = random.choice(self.files_queue)
        else:
            file = self.files_queue[self.files_index % self.files_count]
            self.files_index += 1
        return file

    def get_next_dir(self):
        if self.random_resources:
            dir = random.choice(self.dirs_queue)
        else:
            dir = self.dirs_queue[self.dirs_index % self.dirs_count]
            self.dirs_index += 1
        return dir

    def test_copy_file(self, implementation='python'):

        def _python_copy_file(src, dst):
            dst_path = shutil.copy2(src, dst)
            return dst_path

        def _system_copy_file(src, dst):
            cmd = f'copy /Y "{src}" "{dst}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

        filename = self.get_next_file()
        name, ext = os.path.splitext(filename)
        source_file = os.path.join(self.input_files_path, self.get_next_file())
        source_file_size = os.path.getsize(source_file)

        destination_file = os.path.join(
            self.output_files_path,
            self.generate_unique_filename(
                prefix=f'copied_{name}',
                extension=f'.{ext}'
            )
        )

        operation_details = {
            'op_type': 'copy_file',
            'size': source_file_size,
            'operation_counter': self._operation_counter,
            'path': destination_file
        }

        operation_implementation = _python_copy_file if implementation == 'python' else _system_copy_file
        elapsed, _, success, _ = self.measure_time(operation_implementation, operation_details, src=source_file,
                                                   dst=destination_file)
        self._operation_counter += 1

    def test_copy_dir(self, implementation='python'):

        def _python_copy_dir(src, dst):
            dst_dir = shutil.copytree(src, dst)
            return dst_dir

        def _system_copy_dir(src, dst):
            cmd = ['robocopy', src, dst, '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/NC', '/NS', '/NP']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result

        dir_name = self.get_next_dir()
        source_dir = os.path.join(self.input_dirs_path, dir_name)

        destination_dir = os.path.join(
            self.output_dirs_path,
            self.generate_unique_folder_name(prefix=dir_name)
        )

        operation_details = {
            'op_type': 'copy_dir',
            'size': None,
            'operation_counter': self._operation_counter,
            'path': destination_dir
        }

        operation_implementation = _python_copy_dir if implementation == 'python' else _system_copy_dir
        elapsed, _, success, _ = self.measure_time(operation_implementation, operation_details, src=source_dir,
                                                   dst=destination_dir)
        self._operation_counter += 1

    def test_move_file(self):

        def _python_move_file(src, dst):
            dst_dir = shutil.move(src, dst)
            return dst_dir

        def _system_move_file(src, dst):
            cmd = f'move /Y "{src}" "{dst}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

    def test_edit_text_file(self):

        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=100))

        def _python_edit_text_file(filepath, text):
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text)

        def _system_edit_text_file(filepath, text):
            cmd = f'echo {text} >> "{filepath}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

    def test_read_text_file(self):

        def _python_read_text_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        def _system_read_text_file(filepath):
            cmd = f'type "{filepath}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

    def test_delete_file(self):

        def _python_delete_file(filepath):
            os.remove(filepath)

        def _system_delete_file(filepath):
            cmd = f'del /F /Q "{filepath}"'
            result = subprocess.run(cmd, shell=True)
            return result

    def test_delete_dir(self):

        def _python_delete_dir(path):
            shutil.rmtree(path)

        def _system_delete_dir(path):
            cmd = f'rmdir /S /Q "{path}"'
            result = subprocess.run(cmd, shell=True)
            return result

    def run(self):
        self.test_copy_file()
        self.test_copy_dir()
