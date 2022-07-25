CC=g++
CFLAGS=-O3
EXTRAFLGS=-lpqxx -lpq -pthread
all: serv client
serv: serv.cpp operations.hpp db_operations.cpp xml_operations.cpp tinyxml2.h tinyxml2.cpp
	$(CC) $(CFLAGS) -g -o serv serv.cpp db_operations.cpp xml_operations.cpp tinyxml2.h tinyxml2.cpp $(EXTRAFLGS)
client: client.cpp operations.hpp db_operations.cpp xml_operations.cpp tinyxml2.h tinyxml2.cpp
	$(CC) $(CFLAGS) -g -o client client.cpp db_operations.cpp xml_operations.cpp tinyxml2.h tinyxml2.cpp $(EXTRAFLGS)
.PHONY:
	clean
clean:
	rm -f serv client *.o *~