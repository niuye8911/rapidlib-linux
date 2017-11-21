Minimize
        err

Subject To
s1 - s2 > 1
s2 - s3 > 1
s3 - s4 > 1
s4 - s5 > 1
s5 - s6 > 1

b1 - b2 > 1
b2 - b3 > 1
b3 - b4 > 1
b4 - b5 > 1

s1 + b1 + SYS + comm >= 3241.24
s1 + b1 + SYS + comm - 3241.24 err <= 3241.23

s2 + b5 + SYS + comm >= 2280.96
s2 + b5 + SYS + comm - 2280.96 err <= 2280.96

s4 + b2 + SYS + comm >= 1953.28
s4 + b2 + SYS + comm - 1953.28 err <= 1953.28

s1 + b3 + SYS + comm >= 2736.18
s1 + b3 + SYS + comm - 2736.18 err <= 2736.18

s6 + b1 + SYS + comm >= 1876.4 
s6 + b1 + SYS + comm - 1876.4 err <= 1876.4

s3 + b4 + SYS + comm >= 2062.92
s3 + b4 + SYS + comm - 2062.92 err <= 2062.92

s3 + b2 + SYS + comm >= 2417.81
s3 + b2 + SYS + comm - 2417.81 err <= 2417.81

s4 + b5 + SYS + comm >= 1797.12
s4 + b5 + SYS + comm - 1797.12 err <= 1797.12

s6 + b5 + SYS + comm >= 1676
s6 + b5 + SYS + comm - 1676 err <= 1676

Bounds
err >= 0
err <= 1
s6 > 1
b5 > 1

End
