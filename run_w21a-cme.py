from Board import *

# Create a wrapper for the executable named 'w21a-cme.exe', with table starting
#   at addr 0x407020 of size (8 X 8), where the table row addresses grow up:
p = ProcessWrapper("w21a-cme.exe", 0x407020, 8, 8, vertical_layout=VerticalLayout.BOT_SIDE_LOW_ADDR)


# This module reads the 2 dwords starting at 0x60ff18 and 0x60ff1c, and shows the current player position:
def show_position(wrapper_obj: ProcessWrapper, mem_list: list):
    color_print(f"show_position:\n\tdword list is: {list(map(hex, mem_list))}", color='red')
    
    player_row, player_col = mem_list
    wrapper_obj.cur_data[wrapper_obj.linpos(player_row, player_col)] = ord('P')
p.add_module((0x60ff18, 0x60ff20), show_position, granularity=Granularity.DWORD)


# This module does not read any memory and shows the exit point:
def show_exit_pos(wrapper_obj: ProcessWrapper, _: list = None):
    wrapper_obj.cur_data[wrapper_obj.linpos(7, 0)] = ord('E')
p.add_module(None, show_exit_pos)


p.main_loop()
print("wrapper done")