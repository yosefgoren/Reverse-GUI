from Board import *

p = ProcessWrapper("w21b-cme.exe", 0x407020, 10, 10)

p.main_loop()
print("wrapper done")