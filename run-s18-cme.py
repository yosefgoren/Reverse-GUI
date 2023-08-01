from Board import *

p = ProcessWrapper("main.exe", 0x407020, 0, 0)

base_addr = 0xF2F360
memory_size = 0x2
prev_memory = None

def check_memory(wrapper_obj: ProcessWrapper, mem_list: list):
    print(mem_list)
    global prev_memory
    for index in ProcessWrapper.find_diff_positions(prev_memory, mem_list):
        if prev_memory[index] != mem_list[index]:
            print(f"Found diff at {hex(base_addr+index)}: Prev val - {prev_memory[index]}, New val - {mem_list[index]}")
    prev_memory = mem_list

p.add_module((base_addr, base_addr+memory_size), check_memory, granularity=Granularity.BYTE)

p.main_loop()

print("wrapper done")