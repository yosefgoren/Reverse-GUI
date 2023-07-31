from Board import *

p = ProcessWrapper("w21a-cme.exe", 0x407020, 8, 8, vertical_layout=VerticalLayout.BOT_SIDE_LOW_ADDR)

def show_position(wrapper_obj: ProcessWrapper, mem_list: list):
    color_print(f"show_position:\n\tdword list is: {list(map(hex, mem_list))}", color='red')
    
    player_row, player_col = mem_list
    linear_position = player_col+wrapper_obj.num_cols*player_row
    wrapper_obj.cur_data[linear_position] = ord('P')
p.add_module((0x60ff18, 0x60ff20), show_position, granularity=Granularity.DWORD)

p.main_loop()

print("wrapper done")