#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
""" Default experimenet, will simply detect the flow data
"""
import os
from sadit.Detector import detect
from sadit.util import NetworkLogger

from .Detect import Detect


class DetectRealTime(Detect):
    def init_parser(self, parser):
        super(DetectRealTime, self).init_parser(parser)

        parser.add_argument('--srv', default='',
                            help="<host>:<port> the ip and the port of the "
                            "real-time logging server")

    def detect(self):
        rs = self.args.srv.rsplit(":")
        if len(rs) != 2:
            raise Exception("wrong server address. Input should be "
                            "<host>:<port>")
        real_time_logger = NetworkLogger(dict(url=rs[0], port=int(rs[1])),
                                         'SADIT')
        self.detector = detect(os.path.abspath(self.desc['data']), self.desc,
                               self.res_args,
                               real_time_logger=real_time_logger)
        return self.detector
