class MachineProfile:
    def __init__(self):
        self.metric1s = []
        self.metric2s = []
        self.combineds = []

    def addObservation(self, metric1, metric2, combined):
        self.metric1s.append(metric1)
        self.metric2s.append(metric2)
        self.combineds.append(combined)

    def printToFile(self, output):
        output = open(output, 'w')
        header = False
        if not header:
            metric1 = self.metric1s[0].printAsHeader(',', '', '-1')
            metric2 = self.metric1s[0].printAsHeader(',', '', '-2')
            combined_header = self.metric1s[0].printAsHeader(',', '', '-C')
            output.write(metric1 + "," + metric2 + "," + combined_header +
                         "\n")
            header = True
        for i in range(0, len(self.metric1s)):
            output.write(self.metric1s[i].printAsCSVLine(','))
            output.write(',')
            output.write(self.metric2s[i].printAsCSVLine(','))
            output.write(',')
            output.write(self.combineds[i].printAsCSVLine(','))
            output.write('\n')
        output.close()
