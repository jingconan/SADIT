import sys
sys.path.append("..")
from Detector_basic import detect
from Detector_pcap2netflow import detect_pcap2netflow
try:
    from Detector_SQL import detect_sql
except ImportError as e:
    print '--> cannot import sql related function'
    print '--> e:', e

