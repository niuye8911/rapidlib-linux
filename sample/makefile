CC = g++
CFLAGS =  -std=c++11 -pthread -Wall -g -c
TFLAGS =  -std=c++11 -pthread -Wall -g

INCLUDE = -I/usr/include/curl -I../
LDLIBS = -lcurl

TARGET = test

$(TARGET): ofile ../rsdg.a
	$(CC) $(TFLAGS) -o $@ $< ../rsdg.a $(LDLIBS) $(INCLUDE)

ofile:sample.cpp
	$(CC) $(CFLAGS) -o $@ $< $(INCLUDE)
clean:
	rm $(TARGET)
