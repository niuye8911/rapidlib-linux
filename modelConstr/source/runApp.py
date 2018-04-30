from os import system
def runSwap():
    budget = range(8,80,8)
    print budget
    for i in budget:
        system("bodytrack sequenceB_261 4 261 5000 4 0 1 -rsdg -cont -xml bodytrack_linear.xml -u 26 -b "+str(i))
        system("mv output.txt outputs/output_l_"+str(i)+".txt")
runSwap()