#!/usr/bin/env python
"""Class about parsing data files"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

import _mysql

from DataFile import DataFile
class SQLDataFileWrapper(DataFile):
    """Wrapper the DataFile for real file to SQL server,
    It preloads all the data thus requires large memory"""
    def __init__(self, db_info, fr_win_size, fea_option):
        print 'db_info', db_info
        self.db_info = db_info
        self.db = _mysql.connect(**db_info)
        DataFile.__init__(self, '', fr_win_size, fea_option)

    def parse(self):
        """a functioin to load the data file and store them in **self.flow**
        """
        self.db.query("""SELECT * FROM flows;""")
        r = self.db.store_result()
        result = r.fetch_row(2)
        print 'result, ', result

if __name__ ==  "__main__":
    db_info = dict(
            host = "localhost",
            db = "labeled",
            read_default_file = "~/.my.cnf",
            )
    fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2}
    data_file = SQLDataFileWrapper(db_info, 100, fea_option)

