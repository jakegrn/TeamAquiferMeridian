CC      = gcc
CFLAGS  = -O2 -Wall -std=gnu99
SRC     = src/mrd_ingest.c src/packet.c src/tsstore.c
OBJ     = $(SRC:.c=.o)

all: mrd_ingest

mrd_ingest: $(OBJ)
	$(CC) $(CFLAGS) -o mrd_ingest $(OBJ)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f src/*.o mrd_ingest
