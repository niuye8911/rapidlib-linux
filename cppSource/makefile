CC = g++-7
CFLAGS =  -pthread -Wall -Wno-sign-compare -g -c
TFLAGS =  -pthread -Wall -g

INCLUDE = -I/usr/include/curl
LDLIBS = -lcurl

#dynamic: dynamic.cpp
#	$(info resolving weights...)
#	$(CC) $(TFLAGS) -o $@ $<

all: ./build/rsdg.a

# capsulating into static lib
./build/rsdg.a: rsdg.o rsdggraph.o rsdgparser.o rsdgwrapper.o
	$(info building static library...)
	ar -r -c -s $@ *.o

# top lvl object
rsdg.o: rsdgMission.cpp rapidm.o rsdgservice.o rsdgService.h
	$(info building rsdg Mission...)
	$(CC) $(CFLAGS) $(INCLUDE) $(LDLIBS) -L rsdgservice.o -o $@ $<

# RAPID_M Server
rapidm.o: rapid_m_server.cpp
	$(info building rapid_m client...)
	$(CC) $(CFLAGS) $(INCLUDE) $<

# RSDG Service
rsdgservice.o: rsdgService.cpp
	$(info building rsdg Service...)
	$(CC) $(CFLAGS) -o $@ $<

# C wrapper for rsdgMisison
rsdgwrapper.o: rsdgMissionWrapper.cpp
	$(info building rsdg Mission wrapper...)
	$(CC) $(CFLAGS) $(INCLUDE) $<

# RSDG graph core
rsdggraph.o: RSDG.cpp
	$(info building rsdg Graph...)
	$(CC) $(CFLAGS) -o $@ $<

# XML encoder / decoder
rsdgparser.o: Parser.cpp
	$(CC) $(CFLAGS) -o $@ $<
	$(info Building rsdg Parser...)

clean:
	rm *.o 
	rm build/rsdg.a
