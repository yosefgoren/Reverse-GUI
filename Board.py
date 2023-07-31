import subprocess
import ctypes
from ctypes import wintypes
from colorama import Fore, Back, Style
import time

N_ROWS_LIKE_N_COLS = None

def dbprint(msg, **kwargs):
    if msg is not str:
        msg = str(msg)
    print(Fore.GREEN + msg + Fore.WHITE, **kwargs)

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
		dbprint(self)
                
class ProcessWrapper:
    def __init__(self, path_to_tgt: str, process_args: list, start_addr: int, num_cols: int, num_rows: int, high_row_addr_top: bool = True):
        if process_args is not list:
            process_args = [process_args]
        
        process_args = map(str, process_args)

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start_addr = start_addr
        self.size = num_cols * num_rows

        self.process = subprocess.Popen([path_to_tgt, *process_args], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        #need to define 'process, base_addr, size'

    def read_proccess_memory(self):
        # Get handle to the target process
        process_handle = ctypes.windll.kernel32.OpenProcess(0x0010, False, self.process.pid)

        # Allocate a buffer to store the read bytes
        buffer = ctypes.create_string_buffer(self.size)

        # Read the bytes from the target process's virtual memory
        bytes_read = wintypes.DWORD()
        ctypes.windll.kernel32.ReadProcessMemory(process_handle, self.start_addr, buffer, self.size, ctypes.byref(bytes_read))

        # Close the process handle
        ctypes.windll.kernel32.CloseHandle(process_handle)

        # Convert the buffer tof a list of bytes
        data = list(buffer.raw[:bytes_read.value])
        return data

    def main_loop(self):
        exit_flag = False
        while not exit_flag:
            time.sleep(0.1)
            self.print_board_state()
            cmd, exit_flag = self.get_cmd()
            self.run_cmd(cmd)
        self.print_board_state()

    def get_cmd(self):
        dbprint("pass input: ", end='')
        command = input()+'\n'
        return command, (command == "exit")

    def run_cmd(self, cmd):
        dbprint("Sending command")
        self.process.stdin.write(cmd.encode())
        dbprint("Flushing")
        self.process.stdin.flush()
        # process_out = self.process.stdout.readline()
        # dbprint(process_out.decode())

    def print_board_state(self):
        t = Table(self.num_cols, self.num_rows)
        data=self.read_proccess_memory()
        if not data:
              dbprint("wrapper cannot continue...")
        for cur_row in range(self.num_rows):
            for cur_col in range(self.num_cols):
                curr_val = data[cur_col+cur_row*self.num_cols]
                if curr_val > 9:
                    t.table[cur_row][cur_col] = chr(data[cur_col+cur_row*self.num_cols])
                else:
                    t.table[cur_row][cur_col] = str(data[cur_col+cur_row*self.num_cols])
        dbprint(t)
