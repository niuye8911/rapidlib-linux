gt_output = open('./training_outputs/grountTruth.txt', "r")
mission_output = open("./output.txt", "r")
truth_map = {}
mission_map = {}
totalRound = 0
for line in gt_output:
    col = line.split(':')
    round_num = col[0]
    round_res = float(col[1].split(',')[0])
    truth_map[round_num] = round_res
    totalRound += 1
for line in mission_output:
    col = line.split(':')
    round_num = col[0]
    round_res = float(col[1].split(',')[0])
    mission_map[round_num] = round_res
        # calculate the distortion
toterr = 0.0
for round in range(0, totalRound):
    roundname = "round" + str(round)
    truth_res = truth_map[roundname]
    mission_res = mission_map[roundname]
    error = abs((truth_res - mission_res) / truth_res)
    toterr += error
    # write the average error
meanQoS = 1 - toterr / totalRound
meanQoS = meanQoS * 1000.0 - 999
print(meanQoS)
