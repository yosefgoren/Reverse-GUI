#include <stdio.h>
#include <stdlib.h>

char* tbl;

int main(){
    printf("tbl var is at: 0x%p\n", &tbl);
    tbl = malloc(16);
    printf("tbl var is: 0x%p\n", tbl);
    for(int row = 0; row < 4; ++row){
        for(int col = 0; col < 4; ++col){
            tbl[row*4 + col] = (row == col) ? 'X' : 'O';
        }
    }

    char tmp;
    int ret = !EOF;
    while(ret != EOF){
        ret = scanf("%c", &tmp);
        // printf("%c\n", tmp);
    }

    return 0;
}