import subprocess
import ctypes
from enum import Enum
from ctypes import wintypes
import colorama
from colorama import Fore, Back, Style
import time
import os, signal
import random

N_ROWS_LIKE_N_COLS = None
COLOR_MAP = {
    "green" : Fore.GREEN,
    "red" : Fore.RED,
    "blue" : Fore.BLUE
}

class Granularity(Enum):
    BYTE = 1
    DWORD = 2

class HorizontalLayout(Enum):
    LEFT_SIDE_LOW_ADDR = 1
    RIGHT_SIDE_LOW_ADDR = 2

class VerticalLayout(Enum):
    TOP_SIDE_LOW_ADDR = 1
    BOT_SIDE_LOW_ADDR = 2

class TableIndirection:
    pass

class StaticTableIndirection(TableIndirection):
    pass

class PointerTableIndirection(TableIndirection):
    pass

class HookTableIndirection(TableIndirection):
    def __init__(self, allocation_filter = None):
        """
            default behaviour is to accept any allocation,
            which will mean the first allocation will be treated as the targeted one.

            can also pass arbitrary condition over the allocation index, address and size.
            allocation_filter is a function in the form '(idx: int, addr: int, size: int)->bool'.
        """
        if(allocation_filter is None):
            self.allocation_filter = lambda idx, addr, size: True
        self.allocation_filter = allocation_filter
    
    @staticmethod
    def create_any_match()->bool:
        return HookTableIndirection()

    @staticmethod
    def create_idx_match(wanted_idx: int):
        """
            match allocations with the wanted index (if index is 0 - the first allocation will be matched, etc.)
        """
        return HookTableIndirection(lambda idx, addr, size: idx == wanted_idx)
    
    @staticmethod
    def create_size_match(wanted_size: int):
        """
            match allocations with the wanted size
        """
        return HookTableIndirection(lambda idx, addr, size: size == wanted_size)

def add_random_color(s, seed = None):
    if seed is None:
        seed = ord(s[0])
    colorama.init()
    random.seed(seed)
    color_list = [Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    random_color = random.choice(color_list)
    return f"{random_color}{s}{Style.RESET_ALL}"

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
    else:
        print(color_prefix + msg + Fore.WHITE, **kwargs)

class Table:
    def __init__(self,
            n_cols:int = 8,
            n_rows:int = N_ROWS_LIKE_N_COLS,
            default_value:str = '.',
            horizontal_layout: HorizontalLayout = HorizontalLayout.LEFT_SIDE_LOW_ADDR,
            vertical_layout: VerticalLayout = VerticalLayout.TOP_SIDE_LOW_ADDR    
        ):
        if n_rows == N_ROWS_LIKE_N_COLS:
            n_rows = n_cols

        self.n_cols = n_cols
        self.n_rows = n_rows
        self.rows_list = [[default_value for _ in range(n_cols)] for _ in range(n_rows)]
        
        self.horizontal_layout = horizontal_layout
        self.vertical_layout = vertical_layout
    
    @staticmethod
    def strsum(strlist: list, delim: str)->str:
        res = ""
        for s in strlist:
            res += s+delim
        return res

    @staticmethod
    def sfill(s: str, wanted_size: int)->str:
        while len(s) < wanted_size:
            s += " "
        return s

    def __str__(self) -> str:
        NUM_LEFT_SPACES = 3
        COLUMN_WIDTH = 4

        #define seperator row:
        printable_row_list = []
        seperator_row = " "*NUM_LEFT_SPACES+"+---"*self.n_cols+"+"

        printable_row_list.append(seperator_row)
        for row_idx, row in enumerate(self.rows_list):
            this_row = Table.sfill(str(row_idx), NUM_LEFT_SPACES)+"|"
            for cell in row:
                this_row += " "+add_random_color(cell)+" |"
            if self.horizontal_layout == HorizontalLayout.RIGHT_SIDE_LOW_ADDR:
                this_row = this_row[::-1]
            printable_row_list.append(this_row)
            printable_row_list.append(seperator_row)
        
        if self.vertical_layout == VerticalLayout.BOT_SIDE_LOW_ADDR:
            printable_row_list = printable_row_list[::-1]

        #add index row:
        index_row = " "*(NUM_LEFT_SPACES+2)
        for idx in range(len(self.rows_list[0])):
            effective_idx = idx
            if self.horizontal_layout == HorizontalLayout.RIGHT_SIDE_LOW_ADDR:
                effective_idx = len(self.rows_list[0])-idx
            index_row += Table.sfill(str(effective_idx), COLUMN_WIDTH)
        
        return index_row + "\n" + Table.strsum(printable_row_list, '\n')
        
    def show(self):
        color_print(self)
    
def join_dword(bytes_list: list)->int:
    res = 0
    for byte in bytes_list:
        res = res<<8 | byte
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
    def __init__(self,
            path_to_tgt: str,
            start_addr: int,
            num_cols: int,
            num_rows: int,
            process_args: list = [],
            table_indirection: TableIndirection = StaticTableIndirection(),
            horizontal_layout: HorizontalLayout = HorizontalLayout.LEFT_SIDE_LOW_ADDR,
            vertical_layout: VerticalLayout = VerticalLayout.TOP_SIDE_LOW_ADDR,
            transpose_data: bool = False,
            cell_granularity: Granularity = Granularity.BYTE
        ):
        if type(process_args) is not list:
            process_args = [process_args]
        process_args = map(str, process_args)

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start_addr = start_addr
        if self.start_addr is None:
            self.start_addr = 0
            assert(type(table_indirection) is HookTableIndirection)
        self.size_in_bytes = num_cols*num_rows*(4 if cell_granularity == Granularity.DWORD else 1)

        self.table = Table(self.num_cols, self.num_rows, ' ', horizontal_layout, vertical_layout)
        self.transpose_data = transpose_data
        self.cell_granularity = cell_granularity

        self.table_indirection = table_indirection
        self.prev_data = None
        self.cur_data = None

        self.modules = []
        
        if type(table_indirection) is HookTableIndirection:
            TRACE_DLL_FILENAME = "HeapRead_dll.dll"
            INJECTOR_FILENAME = "Injector.exe" 
            commands_list = [INJECTOR_FILENAME, path_to_tgt, TRACE_DLL_FILENAME, *process_args]
            assert(not start_addr)
        else:
            commands_list = [path_to_tgt, *process_args]
        self.process = subprocess.Popen(commands_list, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.tgt_pid = self.process.pid

        #need to define 'process, base_addr, size'

    def read_proccess_memory(self, start_addr, size):
        # Get handle to the target process
        process_handle = ctypes.windll.kernel32.OpenProcess(0x0010, False, self.tgt_pid)

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
        try:
            time.sleep(0.5)
            exit_flag = False
            while not exit_flag:
                time.sleep(0.1)
                if self.update_data() is False:
                    continue
                
                # try to run modules
                for operation, start, size, granularity in self.modules:
                    try:
                        if start is not None and size is not None:
                            input_array = self.read_proccess_memory(start, size)
                            if granularity == Granularity.DWORD:
                                input_array = convert_little_endian_dwords(input_array)
                            operation(self, input_array)
                        else:
                            operation(self)
                    except Exception as e:
                        color_print(f"failed to run module '{operation.__name__}' due to exception: '{e}'", color='red')

                self.print_board_state()
                cmd, exit_flag = self.get_cmd()
                self.run_cmd(cmd)
            self.print_board_state()
        finally:
            self.process.kill()
            if type(self.table_indirection) is HookTableIndirection:
                color_print(f"tgt_process is {self.tgt_pid}", color='red')
                #kill tgt process
                os.kill(self.tgt_pid, signal.SIGTERM)

    def linpos(self, row_idx: int, col_idx: int)->int:
        if self.transpose_data:
            idx =  self.num_rows*col_idx+row_idx
        else:
            idx =  self.num_cols*row_idx+col_idx
        if self.cell_granularity is Granularity.DWORD:
            idx *= 4
        return idx

    def get_cmd(self):
        color_print("pass input: ", end='')
        command = input()+'\n'
        return command, (command.startswith("exit"))

    def run_cmd(self, cmd):
        color_print("Sending command")
        self.process.stdin.write(cmd.encode())
        color_print("Flushing")
        self.process.stdin.flush()

    def update_data(self)->bool:
        table_addr = None
        if type(self.table_indirection) is StaticTableIndirection:
            table_addr = self.start_addr
        elif type(self.table_indirection) is PointerTableIndirection:
            addr_bytes = self.read_proccess_memory(self.start_addr, 4)
            if len(addr_bytes) != 4:
                color_print(f"could not read pointer to table. pointer addr 0x{self.start_addr:x}", color="red")
                return False
            table_addr = join_dword(addr_bytes[::-1])
        elif type(self.table_indirection) is HookTableIndirection:
            TRACE_DLL_LOG_FILENAME = "trace_dll_log.txt"
            #open file created by hook and read the address from there
            with open(TRACE_DLL_LOG_FILENAME, 'r') as f:
                #read first line:
                tgt_pid = f.readline()
                if not tgt_pid:
                    color_print(f"could not read pid from file '{TRACE_DLL_LOG_FILENAME}'", color="red")
                    return False
                self.tgt_pid = int(tgt_pid, 16)
                
                #each next line is an allocation:
                for idx, line in enumerate(f):
                    addr, size = line.split()
                    addr = int(addr, 16)
                    size = int(size, 16)

                    if self.table_indirection.allocation_filter(idx, addr, size) is True:
                        table_addr = addr
                        break
                
            if table_addr is None:
                color_print(f"none of the allocations matched the filter", color="red")
                return False

        else:
            color_print(f"got unrecognized table indirection type '{self.table_indirection}'", color="red")
            return False

        color_print(f"start is at 0x{self.start_addr:x} table is at 0x{table_addr:x}", color="green")
        self.prev_data = self.cur_data
        self.cur_data = self.read_proccess_memory(table_addr, self.size_in_bytes)
        return True

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
        diff_positions = ProcessWrapper.find_diff_positions(self.cur_data, self.prev_data)

        if not self.cur_data:
              color_print("wrapper cannot continue...", color='red')
              exit(0)

        for cur_row in range(self.num_rows):
            for cur_col in range(self.num_cols):
                lin_pos = self.linpos(cur_row, cur_col)
                curr_val = self.cur_data[lin_pos]
                
                if curr_val > 15 and curr_val<128:
                    self.table.rows_list[cur_row][cur_col] = chr(self.cur_data[lin_pos])
                else:
                    #can change representation to bin() if wanted
                    self.table.rows_list[cur_row][cur_col] = hex(self.cur_data[lin_pos])[2:]
                if lin_pos in diff_positions:
                    self.table.rows_list[cur_row][cur_col] = Fore.RED + self.table.rows_list[cur_row][cur_col] + Fore.BLUE
        print(self.table)


    def add_module(self, input_addr_range: tuple, operation, granularity=Granularity.DWORD):
        """
            'input_addr_range' is a tuple of (start_addr, end_addr) of bytes which will be passed.
            
            'operation' is a function which recives the wrapper object (instance of this class),
            and a list of bytes read from the memory.

            'operation' will likely write to 'wrapper_obj.cur_data'.
        """
        if input_addr_range is None:
            start = None
            size = None
        else:
            if (type(input_addr_range) is not tuple) or (type(input_addr_range[0]) is not int) or (type(input_addr_range[1]) is not int):
                color_print(f"'add_module' expected 'input_addr_range' to be None or a tuple of ints but got: '{input_addr_range}'", color='red')
                exit(1)
            start = input_addr_range[0]
            size = input_addr_range[1]-input_addr_range[0]
        
        self.modules.append((operation, start, size, granularity))
         