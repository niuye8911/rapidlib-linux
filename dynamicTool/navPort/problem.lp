Minimize
        err

Subject To
s1 - s2 > 1
s2 - s3 > 1
s3 - s4 > 1
s4 - s5 > 1
s5 - s6 > 1

info1 - info2 > 1
info2 - info3 > 1

f1 - f2 > 1
f2 - f3 > 1
f3 - f4 > 1
f4 - f5 > 1
f5 - f6 > 1

2198 + s3 + info1 + f3 + SYS + comm + GPS >= 2075
2198 + s3 + info1 + f3 + SYS + comm + GPS - 2075 err <= 2075

2915 + s1 + info2 + f1 + SYS + comm + GPS >= 2280.24
2915 + s1 + info2 + f1 + SYS + comm + GPS - 2280.24 err <= 2280.23

2279 + s2 + info2 + f1 + SYS + comm + GPS >= 2152.24
2279 + s2 + info2 + f1 + SYS + comm + GPS - 2152.24 err <= 2152.23

1796 + s4 + info3 + f4 + SYS + comm >= 1561.24
1796 + s4 + info3 + f4 + SYS + comm - 1561.24 err <= 1561.23

2198 + s3 + info1 + f1 + SYS + comm + GPS >= 2057.24
2198 + s3 + info1 + f1 + SYS + comm + GPS - 2057.24 err <= 2057.23

2915 + info1 + f1 + SYS + comm + GPS >= 2613.24
2915 + info1 + f1 + SYS + comm + GPS - 2613.24 err <= 2613.23

1675 + s6 + info3 + f6 + SYS + comm >= 1374
1675 + s6 + info3 + f6 + SYS + comm - 1374 err <= 1374

1675 + s6 + info3 + f4 + SYS + comm + GPS >= 1829.67
1675 + s6 + info3 + f4 + SYS + comm + GPS - 1829.67 err <= 1829.67

Bounds
err >= 0
err <= 1
s6 > 1
info3 > 1
f6 > 1
2198 = 2198
2915 = 2915
2279 = 2279
1796 = 1796
1675 = 1675

End
