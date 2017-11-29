Maximize
	10 num100000
+	5 num200000
+	3 num300000
+	2 num400000
+	2 num500000
+	1 num600000
+	1 num700000
+	1 num800000
+	1 num900000

Subject To
c1: num100000 + num200000 + num300000 + num400000 + num500000 + num600000 + num700000 + num800000 + num900000 - num = 0

c2: num_0 + num_1 + num_2 + num_3 + num_4 + num_5 + num_6 + num_7 + num_8 - num = 0

c3: num100000 - num_0 = 0
c4: num200000 - num_1 = 0
c5: num300000 - num_2 = 0
c6: num400000 - num_3 = 0
c7: num500000 - num_4 = 0
c8: num600000 - num_5 = 0
c9: num700000 - num_6 = 0
c10: num800000 - num_7 = 0
c11: num900000 - num_8 = 0









c12: 100 num100000
+	50 num200000
+	33.3333 num300000
+	25 num400000
+	20 num500000
+	16.6667 num600000
+	14.2857 num700000
+	12.5 num800000
+	11.1111 num900000
- energy = 0
c13: energy <= 50.000000
c14:num = 1

Bounds
num <= 1
num_0 <= 1
num100000 <= 1
num_1 <= 1
num200000 <= 1
num_2 <= 1
num300000 <= 1
num_3 <= 1
num400000 <= 1
num_4 <= 1
num500000 <= 1
num_5 <= 1
num600000 <= 1
num_6 <= 1
num700000 <= 1
num_7 <= 1
num800000 <= 1
num_8 <= 1
num900000 <= 1

Integers
num
num_0
num100000
num_1
num200000
num_2
num300000
num_3
num400000
num_4
num500000
num_5
num600000
num_6
num700000
num_7
num800000
num_8
num900000

End