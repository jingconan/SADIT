import random
from Detector.AnomalyAna import ModelFreeDetectAnoType
from Detector.AnomalyAna import ModelBaseDetectAnoType

def TypeBlindTest():
    '''Blind Test of Anomaly Type, a anomaly will be randomly generate and we will use
    derivative based method to detect the type of test, get the right ratio'''
    ANOMALY_TYPE_SELECTION_SET = settings_template.ANOMALY_TYPE_SELECTION_SET
    DEGREE_SELECTION_SET = settings_template.DEGREE_SELECTION_SET
    TEST_NUM = settings_template.TEST_NUM

    # TEST_NUM = 1
    mfIndiSet = []
    mbIndiSet = []
    labelSet = []
    for i in xrange(TEST_NUM):
        stTime = now()
        ANOMALY_TYPE = random.choice(ANOMALY_TYPE_SELECTION_SET)
        if ANOMALY_TYPE ==  'FLOW_SIZE':
            DEGREE_SELECTION = random.choice(DEGREE_SELECTION_SET)
            FLOW_SIZE_MEAN= random.randint(1e6, 2e6) if ( DEGREE_SELECTION == 'increase') else random.randint(4e4, 5e4)
            CreateSettings('./settings_template.py', './setting.py',
                        ANOMALY_TYPE = ANOMALY_TYPE,
                        FLOW_SIZE_MEAN = FLOW_SIZE_MEAN)
            ID_SUFFIX = FLOW_SIZE_MEAN
            CateLabel = 1 if ( DEGREE_SELECTION == 'increase') else 2

        elif ANOMALY_TYPE ==  'FLOW_RATE':
            DEGREE_SELECTION = random.choice(DEGREE_SELECTION_SET)
            # FLOW_RATE = random.randrange(1.5, 3, 0.1) if ( DEGREE_SELECTION == 'increase') else random.randrange(0.2, 0.7, 0.1)
            FLOW_RATE = random.choice(np.arange(1.5, 3, 0.1)) if ( DEGREE_SELECTION == 'increase') else random.choice( np.arange(0.2, 0.7, 0.1) )
            CreateSettings('./settings_template.py', './setting.py',
                    ANOMALY_TYPE = ANOMALY_TYPE,
                    FLOW_RATE=FLOW_RATE)
            ID_SUFFIX = FLOW_RATE
            CateLabel = 3 if ( DEGREE_SELECTION == 'increase') else 4


        elif ANOMALY_TYPE == 'ATYPICAL_USER':
            CreateSettings('./settings_template.py', './setting.py',
                    ANOMALY_TYPE = ANOMALY_TYPE)
            ID_SUFFIX = ''
            CateLabel = 5
        else:
            raise ValueError('unknown ANOMATYPE_TYPE')

        print 'start to configure'
        GlobalConfigure()
        print 'start to simulate'
        Simulate()
        print 'start to detect'
        GlobalDetect(settings.OUTPUT_FLOW_FILE, './Share/BlindTest/%d-%s-%s.p'%(i, ANOMALY_TYPE, ID_SUFFIX))
        mfIndi = ModelFreeDetectAnoType()
        mfIndiSet.append(mfIndi)
        mbIndi = ModelBaseDetectAnoType()
        mbIndiSet.append(mbIndi)
        labelSet.append(CateLabel)
        edTime = now()
        print 'test[%d]->total test num:[%d], time for one test:[%d], expected total time:[%d] ' %(i, TEST_NUM, edTime-stTime, (edTime-stTime)*TEST_NUM)
    # LibSVMWrapper(mfIndiSet, mbIndiSet, labelSet)





