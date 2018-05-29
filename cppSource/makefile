CC = g++
CFLAGS =  -std=c++11 -pthread -Wall -g -c
TFLAGS =  -std=c++11 -pthread -Wall -g

INCLUDE = -I/usr/include/curl
LDLIBS = -lcurl

#dynamic: dynamic.cpp
#	$(info resolving weights...)
#	$(CC) $(TFLAGS) -o $@ $<

all: ./build/rsdg.a
./build/rsdg.a: rsdg.o rsdggraph.o rsdgparser.o rsdgwrapper.o
	$(info building static library...)
	ar -r -c -s $@ *.o

rsdg.o: rsdgMission.cpp
	$(info building rsdg Mission...)
	$(CC) $(CFLAGS) $(INCLUDE) $(LDLIBS) -o $@ $<

rsdgwrapper.o: rsdgMissionWrapper.cpp
	$(info building rsdg Mission wrapper...)
	$(CC) $(CFLAGS) $(INCLUDE) $<

rsdggraph.o: RSDG.cpp
	$(info building rsdg Graph...)
	$(CC) $(CFLAGS) -o $@ $<

rsdgparser.o: Parser.cpp
	$(CC) $(CFLAGS) -o $@ $<
	$(info Building rsdg Parser...)

clean:
	rm *.o 
	rm build/rsdg.a
