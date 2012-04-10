#!/usr/bin/env python
from unittest import TestCase, main
from anomaly import *
import sys
sys.path.append("..")
import settings_template as settings

class MyTest(TestCase):
    def testDot(self):
        # pass
        GenAnomalyDot(settings.ANO_DESC, settings.NET_DESC,
                settings.NORM_DESC, settings.OUTPUT_DOT_FILE)


if __name__ == "__main__":
    # main()
    GenAnomalyDot(settings.ANO_DESC, settings.NET_DESC,
                settings.NORM_DESC, settings.OUTPUT_DOT_FILE)
