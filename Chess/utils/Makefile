CC=gcc

all: treelogic.so

treelogic.so: treelogic.c
	$(CC) -shared -fPIC -o treelogic.so treelogic.c -lsqlite3

clear:
	rm treelogic treelogic.so
