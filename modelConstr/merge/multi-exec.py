import sys
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty
import os
import time


def execute(container,id):
    swaptions = '/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps/swaptions/src/swaptions'
    swaptions_multi = '/home/liuliu/Research/parsec-3.0/pkgs/apps/swaptions/inst/amd64-linux.gcc-pthreads/bin/swaptions'
    cmd = [swaptions_multi, '-ns', '100', '-sm', '100000','-nt','4','>','tmp']
    time1 = time.time()
    os.system(" ".join(cmd))
    time2 = time.time()
    container[id] = round((time2 - time1),2)

def main(argv):
    threads = []
    results = [0.]*10
    for i in range(10):
        t = Thread(target=execute, args=(results,i))
        threads.append(t)
        t.start()
    for i in range(10):
        threads[i].join();
    print round(sum(results)/len(results),2)
    print results

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
