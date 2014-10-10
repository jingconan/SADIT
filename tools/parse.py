import re
from time import strptime, mktime

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

def parse_xflow(fileName):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    # Defines the FORMAT of the data file
    FORMAT = dict()
    FORMAT[11] = dict(
        start_time=0,
        proto=2,
        client_ip=3,
        direction=4,
        server_ip=5,
        Cb=7,
        Cp=8,
        Sb=9,
        Sp=10,
        )
    FORMAT[12] = dict(
        start_time=0,
        proto=3,
        client_ip=4,
        direction=5,
        server_ip=6,
        Cb=8,
        Cp=9,
        Sb=10,
        Sp=11,
        )
    FORMAT[13] = dict(
        start_time=0,
        proto=2,
        client_ip=3,
        # client_port=4,
        direction=5,
        server_ip=6,
        # server_port=7,
        Cb=9,
        Cp=10,
        Sb=11,
        Sp=12,
        )
    FORMAT[14] = dict(
        start_time=0,
        proto=3,
        client_ip=4,
        # client_port=5,
        direction=6,
        server_ip=7,
        # server_port=8,
        Cb=10,
        Cp=11,
        Sb=12,
        Sp=13,
        )
    dotted_to_int = lambda x: [int(val) for val in x.rsplit('.')]
    port_str_to_int = lambda x: int(x[1:])
    attr_convert = lambda x: float( x.rsplit('=')[1].rsplit(',')[0] )
    handler = dict(
            start_time = lambda x: mktime(strptime(x, '%Y%m%d.%H:%M:%S')),
            proto = lambda x: x,
            # client_ip = dotted_to_int,
            client_ip = lambda x: x,
            client_port=port_str_to_int,
            direction=lambda x: x,
            # server_ip=dotted_to_int,
            server_ip= lambda x:x,
            server_port=port_str_to_int,
            Cb= attr_convert,
            Cp= attr_convert,
            Sb= attr_convert,
            Sp= lambda x: float(x.rsplit('=')[1].rsplit('\n')[0]),
            )
    fea_name = FORMAT[13].keys()
    fid = open(fileName, 'r')
    t = []
    while True:
        line = fid.readline()
        if not line: break
        item = re.split(' ', line)
        try:
            f = [handler[k](item[v]) for k,v in FORMAT[len(item)].iteritems()]
        except KeyError:
            raise Exception('Unexpected Flow Data Format')
        t.append(f[fea_name.index('start_time')])
        flow.append(f)
    fid.close()

    arg_t = argsort(t)
    sort_flow = [flow[i] for i in arg_t ]

    return sort_flow, fea_name


