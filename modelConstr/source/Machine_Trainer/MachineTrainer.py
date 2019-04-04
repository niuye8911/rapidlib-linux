import random
import socket
import time
import os
import subprocess
import signal
from Classes import AppMethods
from MachineProfile import MachineProfile


class MachineTrainer:
    ENV = {
        "cpu_num": [1, 2, 3, 4],
        "io": [1, 2, 3, 4],
        "vm": [1, 2, 3, 4, 5],
        "vm_bytes": ["512K", "1M", "2M", '5M'],
        "hdd": [1, 2],
        "hdd_bytes": ["100K", "500K", "1M"]
    }

    PCM_PREFIX = [
        '/home/liuliu/Research/pcm/pcm.x', '0.5', '-nc', '-ns', '2>/dev/null',
        '-csv=tmp.csv', '--'
    ]

    TRAINING_TIME = 10

    def __init__(self, training_size=500):
        '''
        Train a machine model based on the measurement
        :param training_size: number of observations
        '''
        self.host_name = socket.gethostname()
        self.TRAINING_SIZE = training_size
        self.training_envs = []
        self.machineProfile = {
        }  # key: two vectors of metrics, value: combined vector

    def train(self):
        '''
        Train the Machine Model using a proper model
        :param machine_file: the path to the machine file (string)
        :return: void, but write the model to the file
        '''
        machine_profile = MachineProfile()
        for i in range(0, self.TRAINING_SIZE):
            print(str(i) + " / " + str(self.TRAINING_SIZE))
            env1_cmd = self.getRandomEnv()
            env2_cmd = self.getRandomEnv()
            # train the first env for 10 seconds
            metric1 = self.trainSingle(env1_cmd)
            print(metric1.metrics['READ'])
            # train the second env for 10 seconds
            metric2 = self.trainSingle(env2_cmd)
            print(metric2.metrics['READ'])
            # train the combined env
            observation = self.trainCombined(env1_cmd, env2_cmd)
            print(observation.metrics['READ'])
            machine_profile.addObservation(metric1, metric2, observation)
        machine_profile.printToFile('machine.csv')

    def trainSingle(self, cmd):
        command = " ".join(MachineTrainer.PCM_PREFIX + cmd +
                           ['-t', str(MachineTrainer.TRAINING_TIME)])
        os.system(command)
        return AppMethods.parseTmpCSV()

    def trainCombined(self, cmd1, cmd2):
        # start the first environment
        env1 = subprocess.Popen(
            " ".join(cmd1), shell=True, preexec_fn=os.setsid)
        # kick in the second environment
        metric = self.trainSingle(cmd2)
        # kill the first environment
        os.killpg(os.getpgid(env1.pid), signal.SIGTERM)
        return metric

    def getRandomEnv(self):
        cpu_num = random.choice(MachineTrainer.ENV['cpu_num'])
        io = random.choice(MachineTrainer.ENV['io'])
        vm = random.choice(MachineTrainer.ENV['vm'])
        vm_bytes = random.choice(MachineTrainer.ENV['vm_bytes'])
        # hdd = random.choice(MachineTrainer.ENV['hdd'])
        # hdd_bytes = random.choice(MachineTrainer.ENV['hdd_bytes'])
        command = [
            '/usr/bin/stress',
            '-q',
            '--cpu',
            str(cpu_num),
            '--io',
            str(io),
            '--vm',
            str(vm),
            '--vm-bytes',
            vm_bytes,
            #    '--hdd',
            #        str(hdd),
            #            '--hdd-bytes',
            #            str(hdd_bytes),
        ]
        return command
