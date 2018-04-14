Minimize
-2 err0 + -2 err1 + -2 err2 + [ err0 ^ 2 + err1 ^ 2 + err2 ^ 2 ]

Subject To
100000 num_0_V + num_0_C + err0 = 237.4
500000 num_1_V + num_1_C + err0 = 1150.2
900000 num_1_V + num_1_C + err0 = 2522.7
500000 num_0_V + num_0_C + err0 = 1150.2
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
