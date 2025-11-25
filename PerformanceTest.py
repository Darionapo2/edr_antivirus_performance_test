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
from operator import index
from sys import prefix


class PerformanceTest:

    def __init__(self, server_id, instance_id, unmonitored_dir='unmonitored', monitored_dir='monitored',
                 random_resources=True):
        self.server_id = server_id
        self.instance_id = instance_id
        self.unmonitored_dir = unmonitored_dir
        self.monitored_dir = monitored_dir
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

        self.copy_folder = os.path.join(self.monitored_dir, 'copy', self.unique_id)
        self.read_folder = os.path.join(self.monitored_dir, 'read', self.unique_id)
        self.write_folder = os.path.join(self.monitored_dir, 'write', self.unique_id)
        self.move_folder = os.path.join(self.monitored_dir, 'move', self.unique_id)

        # delete operation will delete files from the copy operation
        self.delete_folder = self.copy_folder

        folders = [self.copy_folder, self.read_folder, self.write_folder, self.move_folder, self.delete_folder]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

        self._copy_files_index = 0
        self._copy_dirs_index = 0
        self._move_files_index = 0
        self._edit_files_index = 0
        self._read_files_index = 0
        self._delete_files_index = 0
        self._delete_dirs_index = 0

        self.logger = self._setup_logger()

    def _setup_logger(self):
        os.makedirs('logs', exist_ok=True)

        logger = logging.getLogger(self.unique_id)
        logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not logger.handlers:
            fh = logging.FileHandler(f'logs/{self.unique_id}.log', mode="w")
            fh.setFormatter(logging.Formatter(
                '%(asctime)s;%(levelname)s;%(name)s;%(message)s'
            ))

            logger.addHandler(fh)

        return logger

    @staticmethod
    def collect_resources(folder):
        # collecting files
        files = [
            f for f in os.listdir(folder)
            if os.path.isfile(
                os.path.join(folder, f)
            )
        ]
        files = sorted(files)
        n_files = len(files)

        # collecting dirs
        dirs = [
            d for d in os.listdir(folder)
            if not os.path.isfile(
                os.path.join(folder, d)
            )
        ]
        dirs = sorted(dirs)
        n_dirs = len(dirs)

        return files, n_files, dirs, n_dirs

    def get_next_file(self, folder, op):
        files, n_files, _, _ = self.collect_resources(folder)
        if self.random_resources:
            selected_file = random.choice(files)
        else:
            _index = 0
            if op == 'copy':
                _index = self._copy_files_index
                self._copy_files_index += 1
            elif op == 'read':
                _index = self._read_files_index
                self._read_files_index += 1
            elif op == 'move':
                _index = self._move_files_index
                self._move_files_index += 1
            elif op == 'write':
                _index = self._edit_files_index
                self._edit_files_index += 1
            elif op == 'delete':
                _index = self._delete_files_index
                self._delete_files_index += 1

            selected_file = files[_index % n_files]

        return selected_file

    def get_next_dir(self, folder, op):
        _, _, dirs, n_dirs = self.collect_resources(folder)
        if self.random_resources:
            selected_dir = random.choice(dirs)
        else:
            _index = 0
            if op == 'copy':
                _index = self._copy_dirs_index
                self._copy_dirs_index += 1
            elif op == 'delete':
                _index = self._delete_dirs_index
                self._delete_dirs_index += 1

            selected_dir = dirs[_index % n_dirs]

        return selected_dir

    def generate_unique_name(self, prefix, extension):
        timestamp_ns = time.time_ns()
        unique_suffix = f'{timestamp_ns}_{self.pid}_{self._operation_counter:06d}_{uuid.uuid4().hex[:8]}'
        return f'{prefix}_{unique_suffix}{extension}'

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

    def test_copy_file(self, implementation='python'):

        def _python_copy_file(src, dst):
            dst_path = shutil.copy2(src, dst)
            return dst_path

        def _system_copy_file(src, dst):
            cmd = f'copy /Y "{src}" "{dst}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

        filename = self.get_next_file(folder=self.unmonitored_dir, op='copy')
        name, ext = os.path.splitext(filename)
        source_file = os.path.join(self.unmonitored_dir, filename)
        source_file_size = os.path.getsize(source_file)

        destination_file = os.path.join(
            self.copy_folder,
            self.generate_unique_name(
                prefix=f'{name}_copied',
                extension=f'{ext}'
            )
        )

        operation_details = {
            'operation_counter': self._operation_counter,
            'op_type': 'copy_file',
            'size': source_file_size,
            'path': source_file
        }

        operation_implementation = _python_copy_file if implementation == 'python' else _system_copy_file
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details,
                                                   src=source_file, dst=destination_file)

        if success:
            self.logger.info(f'copy_file completed successfully with result: {result}')
        else:
            # TODO: handle error
            pass

        self._operation_counter += 1

    def test_copy_dir(self, implementation='python'):

        def _python_copy_dir(src, dst):
            dst_dir = shutil.copytree(src, dst)
            return dst_dir

        def _system_copy_dir(src, dst):
            cmd = ['robocopy', src, dst, '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/NC', '/NS', '/NP']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result

        dir_name = self.get_next_dir(folder=self.unmonitored_dir, op='copy')
        source_dir = os.path.join(self.unmonitored_dir, dir_name)

        destination_dir = os.path.join(
            self.copy_folder,
            self.generate_unique_name(prefix=f'{dir_name}_copied', extension='')
        )

        operation_details = {
            'op_type': 'copy_dir',
            'size': None,
            'operation_counter': self._operation_counter,
            'path': source_dir
        }

        operation_implementation = _python_copy_dir if implementation == 'python' else _system_copy_dir
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, src=source_dir,
                                                   dst=destination_dir)
        if success:
            self.logger.info(f'copy_dir completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1

    def test_move_file(self, implementation='python'):

        def _python_move_file(src, dst):
            dst_dir = shutil.move(src, dst)
            return dst_dir

        def _system_move_file(src, dst):
            cmd = f'move /Y "{src}" "{dst}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

        dir_name = self.get_next_dir(folder=self.move_folder, op='move')
        source_dir = os.path.join(self.move_folder, dir_name)

        destination_dir = os.path.join(
            self.move_folder,
            self.generate_unique_name(prefix=f'{dir_name}_moved', extension='')
        )

        operation_details = {
            'op_type': 'move_dir',
            'size': None,
            'operation_counter': self._operation_counter,
            'path': source_dir
        }

        operation_implementation = _python_move_file if implementation == 'python' else _system_move_file
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, src=source_dir,
                                                   dst=destination_dir)
        if success:
            self.logger.info(f'move_file completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1


    def test_edit_text_file(self, implementation='python'):

        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=100))

        def _python_edit_text_file(filepath, text):
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text)

        def _system_edit_text_file(filepath, text):
            cmd = f'echo {text} >> "{filepath}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

        filename = self.get_next_file(self.write_folder, op='write')
        filepath = os.path.join(self.write_folder, filename)
        file_size = os.path.getsize(filepath)

        operation_details = {
            'op_type': 'edit_file',
            'size': file_size,
            'operation_counter': self._operation_counter,
            'path': filepath
        }

        operation_implementation = _python_edit_text_file if implementation == 'python' else _system_edit_text_file
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, filepath=filepath,
                                                   text=random_string)
        if success:
            self.logger.info(f'edit_file completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1

    def test_read_text_file(self, implementation='python'):

        def _python_read_text_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        def _system_read_text_file(filepath):
            cmd = f'type "{filepath}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result

        filename = self.get_next_file(self.read_folder, op='read')
        filepath = os.path.join(self.read_folder, filename)
        file_size = os.path.getsize(filepath)

        operation_details = {
            'op_type': 'read_file',
            'size': file_size,
            'operation_counter': self._operation_counter,
            'path': filepath
        }

        operation_implementation = _python_read_text_file if implementation == 'python' else _system_read_text_file
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, filepath=filepath)

        if success:
            self.logger.info(f'read_file completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1

    def test_delete_file(self, implementation='python'):

        def _python_delete_file(filepath):
            os.remove(filepath)

        def _system_delete_file(filepath):
            cmd = f'del /F /Q "{filepath}"'
            result = subprocess.run(cmd, shell=True)
            return result

        filename = self.get_next_file(self.delete_folder, op='delete')
        filepath = os.path.join(self.delete_folder, filename)
        file_size = os.path.getsize(filepath)

        operation_details = {
            'op_type': 'delete_file',
            'size': file_size,
            'operation_counter': self._operation_counter,
            'path': filepath
        }

        operation_implementation = _python_delete_file if implementation == 'python' else _system_delete_file
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, filepath=filepath)

        if success:
            self.logger.info(f'delete_file completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1

    def test_delete_dir(self, implementation='python'):

        def _python_delete_dir(path):
            shutil.rmtree(path)

        def _system_delete_dir(path):
            cmd = f'rmdir /S /Q "{path}"'
            result = subprocess.run(cmd, shell=True)
            return result

        dir_name = self.get_next_dir(self.delete_folder, op='delete')
        path = os.path.join(self.delete_folder, dir_name)

        operation_details = {
            'op_type': 'delete_dir',
            'size': None,
            'operation_counter': self._operation_counter,
            'path': path
        }

        operation_implementation = _python_delete_dir if implementation == 'python' else _system_delete_dir
        elapsed, result, success, _ = self.measure_time(operation_implementation, operation_details, path=path)

        if success:
            self.logger.info(f'delete_dir completed successfully with result: {result}')
        else:
            # TODO: handle errors
            pass

        self._operation_counter += 1

    def run_sequentially(self, iterations=1):
        for i in range(iterations):
            self.test_copy_file(implementation='system')
            self.test_copy_dir(implementation='system')
            self.test_move_file(implementation='system')
            self.test_edit_text_file(implementation='system')
            self.test_read_text_file(implementation='system')
            self.test_delete_file(implementation='system')
            self.test_delete_dir(implementation='system')

        return self.operation_details

    def run_randomly(self, iterations=1):

        operations = [
            self.test_copy_file,
            self.test_copy_dir,
            self.test_move_file,
            self.test_edit_text_file,
            self.test_read_text_file,
            self.test_delete_file,
            self.test_delete_dir,
        ]

        for i in range(iterations):

            # to select a random implementation at each operation
            # implementation = random.choice(['python', 'os'])

            # to select a fixed implementation
            implementation = 'python'

            operation = random.choice(operations)
            operation(implementation=implementation)

        return self.operation_details
