from Board import *

p = ProcessWrapper("w19b-cme.exe", 0x407020, 16, 16, cell_granularity=Granularity.DWORD)
def show_position(wrapper_obj: ProcessWrapper, mem_list: list):
    color_print(f"show_position:\n\tdword list is: {list(map(int, mem_list))}", color='red')
    
    player_col, player_row = mem_list
    wrapper_obj.cur_data[wrapper_obj.linpos(player_row, player_col)] = ord('P')
p.add_module((0x404004, 0x40400C), show_position, granularity=Granularity.DWORD)

p.main_loop()
print("wrapper done")