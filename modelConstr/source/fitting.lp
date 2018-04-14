Minimize
-2 err0 + -2 err1 + -2 err2 + [ err0 ^ 2 + err1 ^ 2 + err2 ^ 2 ]

Subject To
500000 num_0_V + 500000 num_0 + 500000 num_1_V + 500000 num_1 + err0 = 1150.2
100000 num_0_V + 100000 num_0 + 100000 num_1_V + 100000 num_1 + err0 = 237.4
900000 num_0_V + 900000 num_0 + 900000 num_1_V + 900000 num_1 + err0 = 2522.7
num_0 = 1 -> num_0_V = num
num_1 = 0 -> num_1_V = 0
num_1 = 1 -> num_1_V = num
num_0 = 0 -> num_0_V = 0
num_0 + num_1 = 1
Bounds
num_0 <= 1
num_1 <= 1
-99999 <= err0 <= 99999
-99999 <= num_0_V <= 99999
-99999 <= num_1_V <= 99999
-99999 <= num <= 99999
Integers
num_0
num_1
