#!/usr/bin/env python
from Experiment import AttriChangeExper

class ROC(AttriChangeExper):
    """plot ROC curve for the hypothesis test"""
    def __init__(self, settings):
        Experiment.__init__(self, settings)

if __name__ == "__main__":
    import settings
    exper = ROC(settings)
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    # detector.plot_entropy()

