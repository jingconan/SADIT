class BaseDetector(object):
    def set_args(self, argv):
        """set local parameters based on argv"""
        pass
    def print_help(self):
        self.parser.print_help()
        pass
    pass
