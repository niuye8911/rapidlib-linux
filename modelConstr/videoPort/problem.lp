Minimize
err

Subject To
res_1 - res_2 > 1
res_2 - res_3 > 1
fr_1 - fr_2 > 1
fr_2 - fr_3 > 1
fr_3 - fr_4 > 1
scr_1 - scr_2 > 1
scr_2 - scr_3 > 1
scr_3 - scr_4 > 1

res_1 + fr_1 + scr_1 >= 1865.23

res_1 + fr_1 + scr_1 - 1865.23
 err <= 1865.23

res_3 + fr_4 + scr_4 + conn_1 >= 1261.07

res_3 + fr_4 + scr_4 + conn_1 - 1261.07
 err <= 1261.07

res_3 + fr_3 + scr_1 + conn_1 >= 1613.68

res_3 + fr_3 + scr_1 + conn_1 - 1613.68
 err <= 1613.68

res_3 + fr_3 + scr_4 + conn_1 >= 1345.01

res_3 + fr_3 + scr_4 + conn_1 - 1345.01
 err <= 1345.01

res_1 + fr_2 + scr_4 + conn_1 >= 1523.78

res_1 + fr_2 + scr_4 + conn_1 - 1523.78
 err <= 1523.78

res_1 + fr_1 + scr_4 >= 1633.43

res_1 + fr_1 + scr_4 - 1633.43
 err <= 1633.43

res_1 + res_3 - 2 res_2 = 0
scr_1 + scr_3 - 2 scr_2 = 0
scr_2 + scr_4 - 2 scr_3 = 0
End