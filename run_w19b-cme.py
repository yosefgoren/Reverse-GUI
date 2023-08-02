from Board import *

p = ProcessWrapper("w19b-cme.exe", 0x407020, 16, 16, cell_granularity=Granularity.DWORD)
def show_position(wrapper_obj: ProcessWrapper, mem_list: list):
    color_print(f"show_position:\n\tdword list is: {list(map(int, mem_list))}", color='red')
    
    player_col, player_row = mem_list
    wrapper_obj.cur_data[wrapper_obj.linpos(player_row, player_col)] = ord('P')
p.add_module((0x404004, 0x40400C), show_position, granularity=Granularity.DWORD)

def multibyte_notice(wrapper_obj: ProcessWrapper):
    mb_positions = []
    for idx, byte in enumerate(wrapper_obj.cur_data):
        if idx%4 != 0 and byte != 0:
            print(f"row: {(idx//4)//16}, col: {(idx//4)%16}")
p.add_module(None, multibyte_notice, granularity=Granularity.BYTE)

def show_inner_cell(wrapper_obj: ProcessWrapper):
    while True:
        s = input("insert row col byte: ")
        if s in {"e", "exit", ""}:
            break
        row, col, byte = s.split()
        pos = wrapper_obj.linpos(int(row), int(col))+int(byte)
        print(f"value is: {wrapper_obj.cur_data[pos]}")
p.add_module(None, show_inner_cell)


def zero_to_dot(wrapper_obj: ProcessWrapper):
    for idx in range(len(wrapper_obj.cur_data)):
        if wrapper_obj.cur_data[idx] == 0:
            wrapper_obj.cur_data[idx] = ord('.')
p.add_module(None, zero_to_dot, granularity=Granularity.BYTE)

def print_exp_row(wrapper_obj: ProcessWrapper, mem_list: list):
    print(f"req final row: {mem_list[0]}")
p.add_module((0x407420, 0x407424), print_exp_row, granularity=Granularity.DWORD)
def print_exp_col(wrapper_obj: ProcessWrapper, mem_list: list):
    print(f"req final col: {mem_list[0]}")
p.add_module((0x40400C, 0x404010), print_exp_col, granularity=Granularity.DWORD)

p.main_loop()
print("wrapper done")