/home/liuliu/Research/mara_bench/mara_face/facedetect -index /home/liuliu/Research/mara_bench/mara_face/pics/pic_index/full.txt -rsdg -cont -b 10000 -xml ./outputs/facedetect-default.xml

/home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/ferret/obj/amd64-linux.gcc-serial/parsec/bin/ferret-serial /home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/ferret/run/corelnative/ lsh /home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/ferret/run/queries500 50 20 1 output.txt -rsdg -cont -xml ./outputs/ferret-default.xml

/home/liuliu/Research/mara_bench/mara_learn/svm -rsdg -cont -b 10000 -xml ./outputs/svm-default.xml

/home/liuliu/Research/mara_bench/mara_learn/nn -rsdg -cont -b 10000 -xml ./outputs/nn-default.xml

/home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/swaptions/src/swaptions -ns 50 -sm 100 -rsdg -cont -b 10000 -xml ./outputs/swaptions-default.xml

/home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/bodytrack/obj/amd64-linux.gcc-serial/TrackingBenchmark/bodytrack /home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps/bodytrack/run/sequenceB_261/ 4 261 4000 5 4 1 -rsdg -cont -b 10000 -xml ./outputs/bodytrack-default.xml
