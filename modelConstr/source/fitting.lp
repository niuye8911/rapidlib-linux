Minimize
-2 err0 + -2 err1 + -2 err2 + -2 err3 + [ err0 ^ 2 + err1 ^ 2 + err2 ^ 2 + err3 ^ 2 ]

Subject To
500000 num_0_V + num_0_C + err0 = 1150.2
500000 num_1_V + num_1_C + err1 = 1150.2
900000 num_1_V + num_1_C + err3 = 2522.7
100000 num_0_V + num_0_C + err2 = 237.4
Bounds
num_0 <= 1
num_1 <= 1
-99999 <= err3 <= 99999
-99999 <= num_0_C <= 99999
-99999 <= num <= 99999
-99999 <= num_0_V <= 99999
-99999 <= num_1_C <= 99999
-99999 <= err1 <= 99999
-99999 <= err2 <= 99999
-99999 <= err0 <= 99999
-99999 <= num_1_V <= 99999
Integers
num_0
num_1
