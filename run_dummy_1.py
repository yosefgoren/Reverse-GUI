from Board import *

p = ProcessWrapper("dummy_tgt_1.exe", None, 4, 4, table_indirection=HookTableIndirection())

p.main_loop()
print("wrapper done")