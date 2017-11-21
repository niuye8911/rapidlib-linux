Minimize
        err

Subject To

scr1 - scr2 > 1
scr2 - scr3 > 1
scr3 - scr4 > 1
scr4 - scr5 > 1
scr5 - scr6 > 1

inf1 - inf2 > 1
inf2 - inf3 > 1

loc1 - loc2 > 1
loc2 - loc3 > 1
loc3 - loc4 > 1
loc4 - loc5 > 1
loc5 - loc6 > 1

freq1 - freq2 > 1
freq2 - freq3 > 1
scr1 + inf1 + loc1 + freq1 + SYS + comm + GPS >= 1799.38
scr1 + inf1 + loc1 + freq1 + SYS + comm + GPS - 1799.38 err <= 1799.38
scr3 + inf1 + loc3 + freq3 + SYS + comm + GPS >= 1286.04
scr3 + inf1 + loc3 + freq3 + SYS + comm + GPS - 1286.04 err <= 1286.04
scr1 + inf2 + loc1 + freq1 + SYS + comm + GPS >= 1678.86
scr1 + inf2 + loc1 + freq1 + SYS + comm + GPS - 1678.86 err <= 1678.86
scr2 + inf2 + loc1 + freq1 + SYS + comm + GPS >= 1485.21
scr2 + inf2 + loc1 + freq1 + SYS + comm + GPS - 1485.21 err <= 1485.21
scr4 + inf3 + loc4 + freq1 + SYS + comm >= 637.54
scr4 + inf3 + loc4 + freq1 + SYS + comm - 637.54 err <= 637.54


Bounds
err >= 0
err <= 1
scr6 > 1
inf3 > 1
loc6 > 1
freq3 > 1
SYS = 375
comm = 109
GPS = 298



End
