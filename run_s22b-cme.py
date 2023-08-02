from Board import *

p = ProcessWrapper("s22b-cme.exe", None, 5, 7, table_indirection=HookTableIndirection.create_size_match(0x23), process_args=["U"])

p.main_loop()
print("wrapper done")