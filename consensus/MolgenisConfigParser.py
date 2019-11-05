class MolgenisConfigParser:
    def __init__(self, file):
        config = self.parse(file)
        self.server = config['server']
        self.username = config['username']
        self.password = config['password']
        self.prefix = config ['prefix']
        self.consensus= config['consensus']
        self.comments = config['comments']
        self.labs = config['labs']
        self.history = config['history']
        self.previous = config['previous']
        self.input = config['input']
        self.output = config['output']

    @staticmethod
    def parse(file):
        config = {}
        for line in open(file):
            values = line.split('=')
            cfg_list = values[1].replace('\n', '').split(',')
            config[values[0]] = cfg_list[0] if len(cfg_list) == 1 else cfg_list
        return config
