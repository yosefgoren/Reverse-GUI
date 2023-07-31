from Board import *

tgt_path = "cme.exe"
p = ProcessWrapper(tgt_path, 16, 0x408040, 10, 10)
p.main_loop()