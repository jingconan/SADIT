"""  Defines all the wrapper classes for a variety of `data types`
    There are two categrories:
        1. Files in hard disk. the base class is the :class:`PreloadHardDiskFile`.
        2. MySQL database. The base class is the :class:`MySQLDatabase`.
"""
from __future__ import print_function, division, absolute_import
from sadit.util import abstract_method
from sadit.util import Find, DataEndException
class Data(object):
    """abstract base class for data. Data class deals with any implementation
    details of the data. it can be a file, a sql data base, and so on, as long
    as it supports the pure virtual methods defined here.
    """
    def get_rows(self, fields=None, rg=None, rg_type=None):
        """ get a slice of feature

        Parameters
        ---------------
        fields : string or list of string
            the fields we need to get
        rg : list of two floats
            is the range for the slice
        rg_type : str,  {'flow', 'time'}
            type for range

        Returns
        --------------
        list of list

        """
        abstract_method()

    def get_where(self, rg=None, rg_type=None):
        """ get the absolute position of flows records that within the range.

        Find all flows such that its belong to [rg[0], rg[1]). The interval
        is closed in the starting point and open in the ending pont.

        Parameters
        ------------------
        rg : list or tuple or None
            range of the the data. If rg == None, simply return position
            (0, row_num])
        rg_type : {'flow', 'time'}
            specify the type of the range.

        Returns
        -------------------
        sp, ep : ints
            flows with index such that sp <= idx < ed belongs to the range

        """
        abstract_method()

    def get_min_max(self, field_list):
        """  get the min and max value for fields

        Parameters
        ---------------
        field_list : a list of str

        Returns
        --------------
        miN, maX : a list of floats
            the mimium(maximium) value for each field in field_list
        """
        abstract_method()

from sadit.util import np
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
            item = re.split(regular_expression, line)
            # import ipdb;ipdb.set_trace()
            f = tuple(h(item[pos]) for k, pos, h in FORMAT)
            flow.append(f)
    return flow

IP = lambda x:tuple(int(v) for v in x.rsplit('.'))
class PreloadHardDiskFile(Data):
    """ abstract base class for hard disk file """

    RE = None
    """regular expression used to seperate each line into segments"""

    FORMAT = None
    """Format of the Data. Should be a list of tuple, each tuple has 3
    element (field_name, position, converter).
    """

    DT = None
    """ Specify how the data will be stored in Numpy array. Should be np.dtype
    See
    `Numpy.dtype
    <http://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html>`_
    for more information.
    """

    FIELDS = zip(*FORMAT)[0] if FORMAT is not None else None
    """  The name of all columns """

    def __init__(self, f_name):
        """ data_order can be flow_first | feature_first
        """
        self.f_name = f_name
        # self.fields = zip(*self.DT)[0]
        self._init()

    @staticmethod
    def parse(*argv, **kwargv):
        return parse_records(*argv, **kwargv)

    def _init(self):
        # self.fea_vec = ParseRecords(self.f_name, self.FORMAT, self.RE)
        self.fea_vec = self.parse(self.f_name, self.FORMAT, self.RE)
        # import ipdb;ipdb.set_trace()
        self.table = np.array(self.fea_vec, dtype=self.DT)
        self.row_num = self.table.shape[0]

        self.t = np.array([t for t in self.get_rows('start_time')])
        t_idx = np.argsort(self.t)
        self.table = self.table[t_idx]
        self.t = self.t[t_idx]

        self.min_time = min(self.t)
        self.max_time = max(self.t)

    def get_where(self, rg=None, rg_type=None):
        if not rg:
            return 0, self.row_num
        if rg_type == 'flow':
            sp, ep = rg
            if sp >= self.row_num: raise DataEndException()
        elif rg_type == 'time':
            sp = Find(self.t, rg[0]+self.min_time)
            ep = Find(self.t, rg[1]+self.min_time)
            # if rg[1] + self.min_time > self.max_time :
                # import pdb;pdb.set_trace()
                # raise Exception('Probably you set wrong range for normal flows? Go to check DETECTOR_DESC')

            assert(sp != -1 and ep != -1)
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                # import pdb;pdb.set_trace()
                raise DataEndException()
        else:
            raise ValueError('unknow window type')
        return sp, ep

    def get_rows(self, fields=None, rg=None, rg_type=None):
        if fields is None:
            fields = list(self.FIELDS)
        sp, ep = self.get_where(rg, rg_type)
        return self.table[sp:ep][fields]

    def get_min_max(self, feas):
        min_vec = []
        max_vec = []
        for fea in feas:
            dat = self.get_rows(fea)
            min_vec.append(min(dat))
            max_vec.append(max(dat))
        return min_vec, max_vec

class HDF_FS(PreloadHardDiskFile):
    """  Data generated by `fs-simulator
    <http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf>`_ .
    HDF means Hard Disk File.
    """
    RE = '[\[\] :\->]'
    FORMAT = [
            ('start_time', 3, np.float64),
            ('end_time', 4, np.float64),
            ('src_ip', 5, IP),
            ('src_port', 6, np.int16),
            ('dst_ip', 8, IP),
            ('dst_port', 9, np.int16),
            ('prot', 10, np.str_),
            ('node', 12, np.str_),
            ('duration', 13, np.float64),
            ('flow_size', 14, np.float64),
            ]

    DT = np.dtype([
        ('start_time', np.float64, 1),
        ('end_time', np.float64, 1),
        ('src_ip', np.int8, (4,)),
        ('src_port', np.int16, 1),
        ('dst_ip', np.int16, (4,)),
        ('dst_port', np.int16, 1),
        ('prot', np.str_, 5),
        ('node', np.str_ , 5),
        ('duration', np.float64, 1),
        ('flow_size', np.float64, 1),
        ])

import datetime
import time
def str_to_sec(ss, formats):
    """
    >>> str_to_sec('2012-06-17T16:26:18.300868', '%Y-%m-%dT%H:%M:%S.%f')
    14660778.300868
    """
    # x = time.strptime(ss,'%Y-%m-%dT%H:%M:%S.%f')
    x = time.strptime(ss,formats)

    ts = ss.rsplit('.')[1]
    micros = int(ts) if len(ts) == 6 else 0 #FIXME Add microseconds support for xflow
    return datetime.timedelta(
            days = x.tm_yday,
            hours= x.tm_hour,
            minutes= x.tm_min,
            seconds= x.tm_sec,
            microseconds = micros,
            ).total_seconds()


class HDF_Pcap2netflow(PreloadHardDiskFile):
    """Data generated pcap2netflow, softflowd and flowd-reader.

    for more information about pcap2netflow, please visit `pcap2netflow
        <https://bitbucket.org/hbhzwj/pcap2netflow>`_

    See Also
    -------------
    PreloadHardDiskFile
    """

    def IP2(ss):
        return tuple(int(v) for v in ss.rsplit(':')[0][1:-1].rsplit('.'))

    def PORT2(ss):
        return int(ss.rsplit(':')[1])

    RE = ' '
    FORMAT = [
            ('start_time', 2, lambda x: str_to_sec(x, '%Y-%m-%dT%H:%M:%S.%f')),
            ('src_ip', 12, IP2),
            ('src_port', 12, PORT2),
            ('dst_ip', 14, IP2),
            ('dst_port', 14, PORT2),
            ('packets', 16, np.int32),
            ('octets', 18, np.int32),
            ]
    DT = np.dtype([
            ('start_time', np.float64, 1),
            ('src_ip', np.int8, (4,)),
            ('src_port', np.int16, 1),
            ('dst_ip', np.int8, (4,)),
            ('dst_port', np.int16, 1),
            ('packets', np.int64, 1),
            ('octets', np.int64, 1),
        ])



class HDF_FlowExporter(PreloadHardDiskFile):
    """  Data generated FlowExporter. It is a simple tool to convert pcap to
    flow data. It is avaliable in tools folder.

    """
    RE = '[ \n]'
    FORMAT = [
            ('start_time', 0, np.float64),
            ('src_ip', 1, IP),
            ('dst_ip', 2, IP),
            ('prot', 3, np.str_),
            ('flow_size', 4, np.float64),
            ('duration', 5, np.float64),
            ]
    DT = np.dtype([
            ('start_time', np.float64, 1),
            ('src_ip', np.int8, (4,)),
            ('dst_ip', np.int8, (4,)),
            ('prot', np.str_, 5),
            ('flow_size', np.float64, 1),
            ('duration', np.float64, 1),
        ])


def parse_complex_records(fileName, FORMAT, regular_expression):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line: break
        item = re.split(regular_expression, line)
        try:
            f = tuple(h(item[v]) for k,v,h in FORMAT[len(item)])
        except KeyError:
            raise Exception('Unexpected Flow Data Format')
        flow.append(f)
    fid.close()

    return flow

class HDF_Xflow(PreloadHardDiskFile):
    """  Data generated by xflow tool.

    """
    RE = ' '
    DTM = [
        ('start_time', np.float64, 1),
        ('proto', np.str_, 5),
        ('src_ip', np.int8, (4,)),
        ('direction', np.str_, 5),
        ('server_ip', np.int8, (4,)),
        ('Cb', np.float64, 1),
        ('Cp', np.float64, 1),
        ('Sb', np.float64, 1),
        ('Sp', np.float64, 1),
        ]
    FIELDS = zip(*DTM)[0]
    DT = np.dtype(DTM)

    port_str_to_int = lambda x: int(x[1:])
    attr_convert = lambda x: float( x.rsplit('=')[1].rsplit(',')[0] )
    handlers = [
            lambda x: str_to_sec(x, '%Y%m%d.%H:%M:%S'),
            str,
            IP,
            str,
            IP,
            attr_convert,
            attr_convert,
            attr_convert,
            lambda x: float(x.rsplit('=')[1].rsplit('\n')[0]),
            ]
    FORMAT = dict()
    FORMAT[11] = zip(FIELDS, [0, 2, 3, 4, 5, 7, 8, 9, 10], handlers)
    FORMAT[12] = zip(FIELDS, [0, 3, 4, 5, 6, 8, 9, 10, 11], handlers)
    FORMAT[13] = zip(FIELDS, [0, 2, 3, 5, 6, 9, 10, 11, 12], handlers)
    FORMAT[14] = zip(FIELDS, [0, 3, 4, 6, 7, 10, 11, 12, 13], handlers)
    """  FORMAT is a dictionary. The format of xflow is complicated.
    The # of items in each line may chnage. The keys in FORMAT is the #
    of items and value is the corresponding format.
    """

    @staticmethod
    def parse(*argv, **kwargv):
        return parse_complex_records(*argv, **kwargv)



"""  Database Related """

def seq_convert(args, arg_num, handlers):
    res = []
    i = 0;
    for n, h in zip(arg_num, handlers):
        res.append(h(*args[i:(i+n)]))
        i += n
    return tuple(res)

class MySQLDatabase(Data):
    """  MySQL database
    """
    CONV = {}
    """  Used by python _mysql to convert data from string to formats
    See `MySQL user guide <http://mysql-python.sourceforge.net/MySQLdb.html>`_
    """

    TABLE = None
    """  The name for the table that store the flows data.
    """

    FORMAT = {}

    FIELDS = []
    """  The name of all columns """

    def __init__(self, cnf_file):
        self.db = mysql.connect(read_default_file=cnf_file, conv=self.CONV)
        print('successfully connected')
        self._init()

    def query(self, sentence):
        self.db.query(sentence)
        r = self.db.store_result()
        return r.fetch_row(0)

    def select(self, fields, rg=None, rg_type=None):
        SQL_SEN = """SELECT %s FROM %s"""%(fields, self.TABLE) + \
                    self.get_where_SQL(rg, rg_type) + ";"
        # print('SQL_SEN', SQL_SEN)
        return self.query(SQL_SEN)

    def get_min_max(self, fea_list, rg=None, rg_type=None):
        """  fea_list must be a lit
        """
        miN = self.select(','.join(['%s(%s)'%('MIN', f) for f in fea_list]))[0]
        maX = self.select(','.join(['%s(%s)'%('MAX', f) for f in fea_list]))[0]
        return list(miN), list(maX)

    def get_rows(self, fea, rg=None, rg_type=None):
        # get under fields
        mod_flag = False
        if isinstance(fea, str):
            mod_flag = True
            fea = [fea]

        fields = list(itertools.chain(*[self.FORMAT[f][0] for f in fea]))
        arg_num = list(len(self.FORMAT[f][0]) for f in fea)
        handlers = list(self.FORMAT[f][1] for f in fea)

        result = self.select(",".join(fields), rg, rg_type)
        if mod_flag:
            return [seq_convert(r, arg_num, handlers)[0] for r in result]

        return [seq_convert(r, arg_num, handlers) for r in result]

    def get_where_SQL():
        abstract_method()


    def _init(self):
        abstract_method()

##############################################################
####  For simpleweb.org labled dataset, it is stored in ######
####  mysql server.                                     ######
####  visit http://www.simpleweb.org/wiki/Traces for    ######
####  more information (trace 8)                        ######
##############################################################

from sadit.util import mysql, FIELD_TYPE

def long_to_IP(n):
    "convert long int to IP format with a tuple of four ints"

    d = 256 * 256 * 256
    q = []
    while d > 0:
        m,n = divmod(n,d)
        q.append(m)
        d = d // 256
    return tuple(q)

def sec_msec_to_float(sec, msec):
    return float("%s.%s"%(sec, msec))

def float_to_sec_msec(x):
    return [int(x), int( (x-int(x)) * 1e3)]

import itertools
class SperottoIPOM(MySQLDatabase):
    """Data File wrapper for SperottoIPOM2009 format.

    it is stored in mysql server, visit `SperottoIPOM
    <http://traces.simpleweb.org/traces/netflow/netflow2/dataset_description.txt>`_
    for more information.

    +------------+----------------------+------+-----+---------+-------+
    | Field      | Type                 | Null | Key | Default | Extra |
    +------------+----------------------+------+-----+---------+-------+
    | id         | int(10) unsigned     | NO   | PRI | 0       |       |
    +------------+----------------------+------+-----+---------+-------+
    | src_ip     | bigint(20) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | dst_ip     | bigint(20) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | packets    | int(10) unsigned     | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | octets     | int(10) unsigned     | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | start_time | bigint(20) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | start_msec | smallint(6)          | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | end_time   | bigint(20) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | end_msec   | smallint(6)          | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | src_port   | smallint(5) unsigned | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | dst_port   | smallint(5) unsigned | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | tcp_flags  | tinyint(3) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+
    | prot       | tinyint(3) unsigned  | NO   |     | NULL    |       |
    +------------+----------------------+------+-----+---------+-------+

    """
    CONV = {
            FIELD_TYPE.INT24: int,
            FIELD_TYPE.LONG: long,
            FIELD_TYPE.LONGLONG: long,
            }
    TABLE = 'flows_test'

    FORMAT = {
            'start_time': (['start_time', 'start_msec'], sec_msec_to_float),
            'src_ip': (['src_ip'], long_to_IP),
            'dst_ip': (['dst_ip'], long_to_IP),
            'prot': (['prot'], str),
            'packets': (['packets'], int),
            'octets': (['octets'], int),
            }
    FIELDS = ['start_time', 'src_ip', 'dst_ip', 'prot', 'packets']

    def _get_time(self, tp, seq):
        time_tuple = self.query("""SELECT %s_time, %s_msec FROM flows WHERE (id = %d);"""\
                %(tp, tp, seq))[0]
        return float("%s.%s"%(time_tuple))

    def _init(self):
        self.min_time = self._get_time('start', 1)
        self.row_num = self.select('MAX(id)')[0][0]
        self.max_time = self._get_time('start', self.row_num)

    def get_where_SQL(self, rg=None, rg_type=None):
        if rg:
            if rg_type == 'flow':
                SQL_SEN_WHERE = """ WHERE ( (id >= %f) AND (id < %f) )""" %tuple(rg)
                if rg[0] > self.row_num:
                    raise DataEndException("reach data end")

            elif rg_type == 'time':
                st = float_to_sec_msec (rg[0] + self.min_time)
                ed = float_to_sec_msec (rg[1] + self.min_time)
                SQL_SEN_WHERE = """ WHERE ( (start_time > %d) OR ( (start_time = %d) AND (start_msec >= %d)) ) AND
                             ( (end_time < %d) OR ( (end_time = %d) and (end_msec < %d) ) )""" %(st[0], st[0], st[1], ed[0], ed[0], ed[1])

                if rg[0] + self.min_time > self.max_time:
                    raise DataEndException("reach data end")
            else:
                print('rg_type', rg_type)
                raise ValueError('unknow window type')
        else:
            SQL_SEN_WHERE = ""
        return SQL_SEN_WHERE


if __name__ == "__main__":
    import doctest
    doctest.testmod()

