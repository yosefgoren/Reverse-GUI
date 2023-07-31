import subprocess
import ctypes
from enum import Enum
from ctypes import wintypes
from colorama import Fore, Back, Style
import time

N_ROWS_LIKE_N_COLS = None
COLOR_MAP = {
    "green" : Fore.GREEN,
    "red" : Fore.RED,
    "blue" : Fore.BLUE
}

def color_print(msg, **kwargs):
    color_prefix = Fore.GREEN
    if 'color' in kwargs:
        color_flag = kwargs['color']
        if color_flag in COLOR_MAP:
            color_prefix = COLOR_MAP[kwargs['color']]
        else:
            print(f"'color_print' got unrecognized color flag: '{color_flag}'")
        del kwargs['color']

    if msg is not str:
        msg = str(msg)
    print(color_prefix + msg + Fore.WHITE, **kwargs)

class Table:
	def __init__(self, n_cols:int=8, n_rows:int=N_ROWS_LIKE_N_COLS, default_value:str = '.'):
		if n_rows == N_ROWS_LIKE_N_COLS:
			n_rows = n_cols
		self.n_cols = n_cols
		self.n_rows = n_rows
		self.table = [[default_value for _ in range(n_cols)] for _ in range(n_rows)]
	
	def __str__(self) -> str:
		seperator_row = "+---"*self.n_cols+"+"+"\n"
		res = seperator_row
		for row in self.table:
			res += "|"
			for cell in row:
				res += " "+cell+" |"
			res += "\n"
			res += seperator_row
		return res

	def show(self):
		color_print(self)
    

class Granularity(Enum):
    BYTE = 1
    DWORD = 2

def join_dword(bytes_list: list)->int:
    res = 0
    for byte in bytes_list:
        res = res<<2 | byte
    return res 

def convert_little_endian_dwords(bytes_list: list)->list:
    if len(bytes_list)%4 != 0:
        raise "expected multiple of 4 in byte list"
    dword_list = []
    for i in range(0, len(bytes_list), 4):
        ordered_bytes = bytes_list[i:i+4][::-1]
        next_dword = join_dword(ordered_bytes)
        dword_list.append(next_dword)

    return dword_list
                
class ProcessWrapper:
    def __init__(self, path_to_tgt: str, process_args: list, start_addr: int, num_cols: int, num_rows: int, high_row_addr_top: bool = True):
        if process_args is not list:
            process_args = [process_args]
        
        process_args = map(str, process_args)

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start_addr = start_addr
        self.size = num_cols * num_rows

        self.prev_data = None
        self.cur_data = None

        self.modules = []

        self.process = subprocess.Popen([path_to_tgt, *process_args], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        #need to define 'process, base_addr, size'

    @staticmethod
    def read_proccess_memory(pid, start_addr, size):
        # Get handle to the target process
        process_handle = ctypes.windll.kernel32.OpenProcess(0x0010, False, pid)

        # Allocate a buffer to store the read bytes
        buffer = ctypes.create_string_buffer(size)

        # Read the bytes from the target process's virtual memory
        bytes_read = wintypes.DWORD()
        ctypes.windll.kernel32.ReadProcessMemory(process_handle, start_addr, buffer, size, ctypes.byref(bytes_read))

        # Close the process handle
        ctypes.windll.kernel32.CloseHandle(process_handle)

        # Convert the buffer tof a list of bytes
        data = list(buffer.raw[:bytes_read.value])
        return data

    def main_loop(self):
        exit_flag = False
        while not exit_flag:
            time.sleep(0.1)
            self.update_data()
            
            # try to run modules
            for operation, start, size, granularity in self.modules:
                try:
                    input_array = ProcessWrapper.read_proccess_memory(self.process.pid, start, size)
                    if granularity == Granularity.DWORD:
                        input_array = convert_little_endian_dwords(input_array)
                    operation(self, input_array)
                except Exception as e:
                    color_print(f"failed to run module '{operation.__name__}' due to exception: '{e}'", color='red')

            self.print_board_state()
            cmd, exit_flag = self.get_cmd()
            self.run_cmd(cmd)
        self.print_board_state()

    def get_cmd(self):
        color_print("pass input: ", end='')
        command = input()+'\n'
        return command, (command == "exit")

    def run_cmd(self, cmd):
        color_print("Sending command")
        self.process.stdin.write(cmd.encode())
        color_print("Flushing")
        self.process.stdin.flush()
        # process_out = self.process.stdout.readline()
        # color_print(process_out.decode())

    def update_data(self):
        self.prev_data = self.cur_data
        self.cur_data = ProcessWrapper.read_proccess_memory(self.process.pid, self.start_addr, self.size)

    @staticmethod
    def find_diff_positions(nested_ls_a: list, nested_ls_b: list)->set:
        if nested_ls_a is None or nested_ls_b is None:
             return set()
        
        res = set()
        for idx, (a, b) in enumerate(zip(nested_ls_a, nested_ls_b)):
            if a != b:
                res.add(idx)
        return res

    def print_board_state(self):
        t = Table(self.num_cols, self.num_rows)
        
        diff_positions = ProcessWrapper.find_diff_positions(self.cur_data, self.prev_data)

        if not self.cur_data:
              color_print("wrapper cannot continue...", color='red')
              exit(0)

        for cur_row in range(self.num_rows):
            for cur_col in range(self.num_cols):
                lin_pos = cur_col+cur_row*self.num_cols
                curr_val = self.cur_data[lin_pos]
                if curr_val > 9:
                    t.table[cur_row][cur_col] = chr(self.cur_data[lin_pos])
                else:
                    t.table[cur_row][cur_col] = str(self.cur_data[lin_pos])
                if lin_pos in diff_positions:
                    t.table[cur_row][cur_col] = Fore.RED + t.table[cur_row][cur_col] + Fore.BLUE
        color_print(t, color='blue')


    def add_module(self, input_addr_range: tuple, operation, granularity=Granularity.DWORD):
        """
            'input_addr_range' is a tuple of (start_addr, end_addr) of bytes which will be passed.
            
            'operation' is a function which recives the wrapper object (instance of this class),
            and a list of bytes read from the memory.

            'operation' will likely write to 'wrapper_obj.cur_data'.
        """
        if (type(input_addr_range) is not tuple) or (type(input_addr_range[0]) is not int) or (type(input_addr_range[1]) is not int):
            color_print(f"'add_module' expected 'input_addr_range' to be a tuple of ints but got: '{input_addr_range}'", color='red')
            exit(1)
        start = input_addr_range[0]
        size = input_addr_range[1]-input_addr_range[0]
        
        self.modules.append((operation, start, size, granularity))
         