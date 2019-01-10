import random

time =[]
with open ('./tmp.txt') as file:
	for line in file:
		col = line.split()
		time.append(float(col[0]))

sampletimes = []

for i in range(1,11):
	times = random.sample(time,20)
	total = sum(times)
	sampletimes.append(total * 20 / 1000)

print sum(sampletimes)/10.0
