Minimize
	865 100p
+	672 80p
+	399 50p
+	151 20p
+	0 10p
+	1516 720p
+	963 480p
+	885 360p
+	831 240p
+	742 144p
+	375 sys
+	109 comm

Subject To
c1: 100p + 80p + 50p + 20p + 10p - screen = 0
c2: 720p + 480p + 360p + 240p + 144p - quality = 0
c3: sys - sys = 0
c4: comm - comm = 0

c5: screen_0 + screen_1 + screen_2 + screen_3 + screen_4 - screen = 0
c6: quality_0 + quality_1 + quality_2 + quality_3 + quality_4 - quality = 0
c7: sys_0 - sys = 0
c8: comm_0 - comm = 0

c9: 100p - screen_0 = 0
c10: 80p - screen_1 = 0
c11: 50p - screen_2 = 0
c12: 20p - screen_3 = 0
c13: 10p - screen_4 = 0
c14: 720p - quality_0 = 0
c15: 480p - quality_1 = 0
c16: 360p - quality_2 = 0
c17: 240p - quality_3 = 0
c18: 144p - quality_4 = 0
c19: sys - sys_0 = 0
c20: comm - comm_0 = 0












c21: 25 100p
+	20 80p
+	15 50p
+	10 20p
+	5 10p
+	5 720p
+	4 480p
+	3 360p
+	2 240p
+	1 144p
+	0 sys
+	0 comm
- mv = 0
c22: mv >= 30.000000
c23:sys = 1
c24:comm = 1
c25:screen = 1
c26:quality = 1

Bounds
screen <= 1
screen_0 <= 1
100p <= 1
screen_1 <= 1
80p <= 1
screen_2 <= 1
50p <= 1
screen_3 <= 1
20p <= 1
screen_4 <= 1
10p <= 1
quality <= 1
quality_0 <= 1
720p <= 1
quality_1 <= 1
480p <= 1
quality_2 <= 1
360p <= 1
quality_3 <= 1
240p <= 1
quality_4 <= 1
144p <= 1
sys <= 1
sys_0 <= 1
sys <= 1
comm <= 1
comm_0 <= 1
comm <= 1

Integers
screen
screen_0
100p
screen_1
80p
screen_2
50p
screen_3
20p
screen_4
10p
quality
quality_0
720p
quality_1
480p
quality_2
360p
quality_3
240p
quality_4
144p
sys
sys_0
sys
comm
comm_0
comm

End