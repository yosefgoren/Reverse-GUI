from Board import *

p = ProcessWrapper("dummy_tgt_1.exe", 0x407070, 4, 4, table_indirection=TableIndirection.POINTER)

p.main_loop()
print("wrapper done")