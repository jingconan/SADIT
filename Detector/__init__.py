from AnomalyDetector import detect
try:
    from SQLDetector import detect_sql
except ImportError:
    print '--> cannot import sql related function'

