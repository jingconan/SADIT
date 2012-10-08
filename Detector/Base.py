class BaseDetector(object):
    def set_args(self, argv):
        """set local parameters based on argv"""
        pass

    def init_parser(self, parser):
        pass

    def detect(self, data_file):
        """detect data_file"""
        pass
