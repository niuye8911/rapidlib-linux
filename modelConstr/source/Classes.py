# configuration consists of multiple config's, each of which represents a setting for a knob
class Configuration:
    def __init__(self):
        self.knobs = []
    def addConfig(self,config):
        for c in config:
            self.knobs.append(c)

# a config for a certain knob
class config:
    def __init__(self,setting,val):
        self.setting = setting
        self.val = val

# a continuous constraint
class constraint:
    def __init__(self,type,source,sink,source_min,source_max,sink_min,sink_max):
        self.type = type
        self.source = source
        self.sink = sink
        self.source_min = int(source_min)
        self.source_max = int(source_max)
        self.sink_min = int(sink_min)
        self.sink_max = int(sink_max)

# a knob setting
class knob:
    def __init__(self,svc_name,set_name,min,max):
        self.svc_name = svc_name
        self.set_name = set_name
        self.min = int(min)
        self.max = int(max)