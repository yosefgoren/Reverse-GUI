from Board import *

args = ["w21b-cme.exe", [], 0x407020, 10, 10]

p = ProcessWrapper(*args)
p.main_loop()
print("wrapper done")