def IP(x):
    return tuple(int(v) for v in x.rsplit('.'))

import re
def parse_records(f_name, FORMAT, regular_expression):
    flow = []
    with open(f_name, 'r') as fid:
        while True:
            line = fid.readline()
            if not line:
                break
            if line == '\n': # Ignore Blank Line
                continue
            line = line.strip()
            item = re.split(regular_expression, line)
            f = tuple(h(item[pos]) for k, pos, h in FORMAT)
            flow.append(f)
    return flow


from libc.stdio cimport *
import numpy as np
cimport numpy as np

cdef extern from "stdio.h":
    FILE *fopen   (const_char *FILENAME, const_char  *OPENTYPE)
    int fscanf   (FILE *STREAM, const_char *TEMPLATE, ...)
    enum: EOF
    # int sscanf   (const_char *S, const_char *TEMPLATE, ...)
    # int printf   (const_char *TEMPLATE, ...)

DEF MAX_ROW = 3000

def c_parse_records_fs(const_char *f_name):
    cdef int node_id
    cdef char[10] prot
    cdef char[10] node
    cdef int duration
    cdef FILE* cfile
    cdef double start_time, end_time
    cdef double t3
    cdef int s1, s2, s3, s4
    cdef int d1, d2, d3, d4
    cdef int port1, port2
    cdef int flow_size

    cdef np.ndarray flows = np.ndarray((MAX_ROW,), dtype= np.dtype([
        ('start_time', np.float64, 1),
        ('end_time', np.float64, 1),
        ('src_ip', np.uint8, (4,)),
        ('src_port', np.int16, 1),
        ('dst_ip', np.uint8, (4,)),
        ('dst_port', np.int16, 1),
        ('prot', np.str_, 5),
        ('node', np.str_ , 5),
        ('flow_size', np.float64, 1),
        ('duration', np.float64, 1),
        ])
    )

    cfile = fopen(f_name, 'r') # attach the stream
    i = -1
    while True:
        i += 1
        if i > MAX_ROW:
            raise Exception("MAX_ROW too SMALL! Please increase MAX_ROW in "
                            "CythonUtil.pyx")

        value = fscanf(cfile, 
               'textexport n%i '
               '%lf %lf %lf %i.%i.%i.%i:%i->%i.%i.%i.%i:%i %s 0x0 '
               '%s %i %i FSA\n',
                &node_id, 
                &start_time, &end_time, &t3, 
                &s1, &s2, &s3, &s4, &port1,
                &d1, &d2, &d3, &d4, &port2,
                &prot[0], &node[0], 
                &duration,
                &flow_size
                )

        if value == EOF:
            break
        elif value != 18:
            raise Exception("value = " + str(value))

        flows[i] = (start_time, end_time, (s1, s2, s3, s4), port1, 
                (d1, d2, d3, d4), port2, prot, node, flow_size, duration)

        # printf('textexport n%i '
        #        '%lf %lf %lf %i.%i.%i.%i:%i->%i.%i.%i.%i:%i tcp 0x0 '
        #        '%s %i %i FSA\n',
        #         node_id, 
        #         start_time2, end_time2, t3, 
        #         s1, s2, s3, s4, port1,
        #         d1, d2, d3, d4, port2,
        #         prot, tp_unknown,
        #         flow_size
        #         ) 

        # break
    # print 'hello world'
    return flows
