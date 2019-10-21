"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Rapids_Classes.AppMethods import AppMethods  # import the parent class and other classes from the
import os
import numpy as np


class appMethods(AppMethods):
    base_path = "/home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps" \
                 "/x264/"
    input_path = base_path + "inputs/eledream_1920x1080_512.y4m"
    output_file_name = "eledream.264"
    training = False

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 100
        self.fullrun_units = 512
        self.max_cost = 0
        self.min_cost = 0
        self.min_mv = 0
        self.max_mv = 0
        self.run_config_file = "./outputs/x264/x264_run.config"

    def cleanUpAfterEachRun(self, configs=None):
        # backup the generated output to another location
        control_rate = 50
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "rate":
                    control_rate = config.val  # retrieve the setting for each knob
        self.moveFile(
            self.output_file_name,
            "./training_outputs/x264/output_" + str(control_rate) + ".txt")

    def afterGTRun(self):
        pass

    def getRapidsCommand(self):
        if not os.path.exists(self.run_config):
            print("no config file exists:", self.appName, self.run_config)
            return []
        self.training = False
        cmd = [
            self.obj_path, '--qp 20', '--partitions b8x8,i4x4', '--ref 5',
            '--direct auto', '--weightb --mixed-refs --no-fast-pskip',
            '--me umh', '--subme 7', '--analyse b8x8,i4x4', '--threads 1',
            '-o', self.output_file_name, '--rsdg', self.run_config,
            self.input_path
        ]
        return cmd

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=True):
        if qosRun:
            return []
        control_rate = 50
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "rate":
                    control_rate = config.val  # retrieve the setting for each knob
        if fullRun or qosRun:
            total_frame = self.fullrun_units
            self.training = False
        else:
            self.training = True
            total_frame = self.training_units
        cmd = [
            self.obj_path, '--qp 20', '--frames ' + str(total_frame),
            '--partitions b8x8,i4x4', '--ref 5', '--direct auto',
            '--weightb --mixed-refs --no-fast-pskip', '--me umh', '--subme 7',
            '--analyse b8x8,i4x4', '--threads 1', '-o', self.output_file_name,
            '--rate',
            str(control_rate), self.input_path
        ]
        return cmd

    def getQoS(self):
        result = open('./summary.txt', 'r')
        # call evaluate routine
        try:
            # check the file size
            output_size = os.path.getsize(self.output_file_name) / 1000.0
            input_size = os.path.getsize(self.input_path) / 1000.0
            if self.training:
                input_size = input_size * self.training_units / self.fullrun_units
            for line in result:
                col = line.split(':')
                if 'SSIM' in col[0]:
                    ssim = float(col[1])
                if 'PSNR' in col[0]:
                    psnr = float(col[1])
        except:
            return [0.0, 0.0, 0.0, 0.0]
        return [ssim, psnr, compress_rate, psnr]
