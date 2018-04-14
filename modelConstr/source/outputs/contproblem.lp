Minimize
-2 err1 + -2 err2 + [ err1 ^ 2 + err2 ^ 2 ]

Subject To
10000000000.0 num_2 + 100000.0 num_1 + num_c +  -237.4 err1 = 0
1e+12 num_2 + 1000000.0 num_1 + num_c +  -2316.2 err2 = 0
Bounds 
-99999 < num_1 < 99999
0 < num_2
-99999 < num_c < 99999
-99999 < err1 < 99999
-99999 < err2 < 99999
