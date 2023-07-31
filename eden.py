data_dump = """.bss:00408041 db  57h ; W
.bss:00408041 db  57h ; W
.bss:00408042 db  57h ; W
.bss:00408043 db  57h ; W
.bss:00408044 db  57h ; W
.bss:00408045 db  57h ; W
.bss:00408046 db  57h ; W
.bss:00408047 db  57h ; W
.bss:00408048 db  57h ; W
.bss:00408049 db  57h ; W
.bss:0040804A db  57h ; W
.bss:0040804B db  2Eh ; .
.bss:0040804C db  2Eh ; .
.bss:0040804D db  2Eh ; .
.bss:0040804E db  2Eh ; .
.bss:0040804F db  2Eh ; .
.bss:00408050 db  2Eh ; .
.bss:00408051 db  2Eh ; .
.bss:00408052 db  2Eh ; .
.bss:00408053 db  57h ; W
.bss:00408054 db  57h ; W
.bss:00408055 db  2Eh ; .
.bss:00408056 db  2Eh ; .
.bss:00408057 db  2Eh ; .
.bss:00408058 db  2Eh ; .
.bss:00408059 db  2Eh ; .
.bss:0040805A db  2Eh ; .
.bss:0040805B db  2Eh ; .
.bss:0040805C db  2Eh ; .
.bss:0040805D db  57h ; W
.bss:0040805E db  57h ; W
.bss:0040805F db  2Eh ; .
.bss:00408060 db  2Eh ; .
.bss:00408061 db  2Eh ; .
.bss:00408062 db  2Eh ; .
.bss:00408063 db  2Eh ; .
.bss:00408064 db  2Eh ; .
.bss:00408065 db  2Eh ; .
.bss:00408066 db  2Eh ; .
.bss:00408067 db  57h ; W
.bss:00408068 db  57h ; W
.bss:00408069 db  2Eh ; .
.bss:0040806A db  57h ; W
.bss:0040806B db  2Eh ; .
.bss:0040806C db  2Eh ; .
.bss:0040806D db  2Eh ; .
.bss:0040806E db  2Eh ; .
.bss:0040806F db  57h ; W
.bss:00408070 db  2Eh ; .
.bss:00408071 db  57h ; W
.bss:00408072 db  57h ; W
.bss:00408073 db  50h ; P
.bss:00408074 db  57h ; W
.bss:00408075 db  2Eh ; .
.bss:00408076 db  2Eh ; .
.bss:00408077 db  2Eh ; .
.bss:00408078 db  2Eh ; .
.bss:00408079 db  57h ; W
.bss:0040807A db  4Bh ; K
.bss:0040807B db  57h ; W
.bss:0040807C db  57h ; W
.bss:0040807D db  4Bh ; K
.bss:0040807E db  57h ; W
.bss:0040807F db  2Eh ; .
.bss:00408080 db  2Eh ; .
.bss:00408081 db  2Eh ; .
.bss:00408082 db  2Eh ; .
.bss:00408083 db  57h ; W
.bss:00408084 db  2Eh ; .
.bss:00408085 db  57h ; W
.bss:00408086 db  57h ; W
.bss:00408087 db  57h ; W
.bss:00408088 db  57h ; W
.bss:00408089 db  2Eh ; .
.bss:0040808A db  2Eh ; .
.bss:0040808B db  2Eh ; .
.bss:0040808C db  2Eh ; .
.bss:0040808D db  57h ; W
.bss:0040808E db  57h ; W
.bss:0040808F db  57h ; W
.bss:00408090 db  57h ; W
.bss:00408091 db  2Eh ; .
.bss:00408092 db  2Eh ; .
.bss:00408093 db  2Eh ; .
.bss:00408094 db  2Eh ; .
.bss:00408095 db  48h ; H
.bss:00408096 db  2Eh ; .
.bss:00408097 db  2Eh ; .
.bss:00408098 db  2Eh ; .
.bss:00408099 db  57h ; W
.bss:0040809A db  57h ; W
.bss:0040809B db  57h ; W
.bss:0040809C db  57h ; W
.bss:0040809D db  57h ; W
.bss:0040809E db  57h ; W
.bss:0040809F db  57h ; W
.bss:004080A0 db  57h ; W
.bss:004080A1 db  57h ; W
.bss:004080A2 db  57h ; W
.bss:004080A3 db  57h ; W"""


def print_board(square_size):
    board = []

    letters = [l[-1] for l in data_dump.split("\n")]

    for i in range(10):
        for j in range(10):
            print(letters[i*10+j], end = " ")
        print()

print_board(10)


