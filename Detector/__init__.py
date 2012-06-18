import sys
sys.path.append("..")
from Detector_basic import detect
try:
    from Detector_SQL import detect_sql
except ImportError:
    print '--> cannot import sql related function'

