Minimize
err

Subject To
itr_1 - itr_2 > 1
L_1 - L_2 > 1
L_2 - L_3 > 1
T_1 - T_2 > 1
T_2 - T_3 > 1
T_3 - T_4 > 1

L_1 + T_1 + itr_1 >= 125

L_1 + T_1 + itr_1 - 125
 err <= 125

L_3 + T_4 + itr_2 >= 52

L_3 + T_4 + itr_2 - 52
 err <= 52

L_1 + T_2 + itr_2 >= 98

L_1 + T_2 + itr_2 - 98
 err <= 98

L_1 + T_2 + itr_1 >= 114

L_1 + T_2 + itr_1 - 114
 err <= 114

L_3 + T_2 + itr_1 >= 81

L_3 + T_2 + itr_1 - 81
 err <= 81

L_1 + L_3 - 2 L_2 = 0
T_2 + T_4 - 2 T_3 = 0
End