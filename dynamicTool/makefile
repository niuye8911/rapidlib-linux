CC = g++
CFLAGS =  -std=c++11 -pthread -Wall -g -c
TFLAGS =  -std=c++11 -pthread -Wall -g

INCLUDE = -I/usr/lib/curl/build/include
LDFLAGS = -L/usr/lib/curl/build/lib
LDLIBS = -lcurl

dynamic: dynamic.cpp gen
	$(info resolving weights...)
	$(CC) $(TFLAGS) -o $@ $<

gen: generate.cpp
	$(info generating observe file)
	$(CC) $(TFLAGS) -o $@ $<

clean:
	rm *.o *.a
