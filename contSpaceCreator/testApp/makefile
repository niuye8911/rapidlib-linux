CC = g++
CFLAGS =  -std=c++11 -pthread -Wall -g -c
TFLAGS =  -std=c++11 -pthread -Wall -g

INCLUDE = -I /Users/liuliu/Documents/rapidlib-linux 
LDLIBS = -lcurl
TARGET = test

$(TARGET): ofile ../../rsdg.a
	$(CC) $(TFLAGS) -o $@ $< ../../rsdg.a $(LDLIBS) $(INCLUDE)

ofile:checkTime.cpp
	$(CC) $(CFLAGS) -o $@ $< $(INCLUDE)
clean:
	rm $(TARGET)
