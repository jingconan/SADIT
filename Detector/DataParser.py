#!/usr/bin/env python
# Copyright (C)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

##
# @file DataParser.py
# @brief Parse Flow data
# @author Jing Conan Wang, hbhzwj@gmail.com
# @version 0.0
# @date 2011-10-25


# Format for returned result flow
# flow is a list of dictionary
# dictionary has the following field
# t - Time of the start of the flow
# srcIPStr - the dotted string of src IP address
# srcIP - the long int representation of src IP address
# srcPort - Port number of source
# destIPStr - the dotted string of dest IP address
# destIP - the long int representation of dest IP address
# destPort - port number at the destination


def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"

    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
    return long(hexn, 16)

def numToDottedQuad(n):
    "convert long int to dotted quad string"

    d = 256 * 256 * 256
    q = []
    while d > 0:
        m,n = divmod(n,d)
        q.append(str(m))
        d = d/256

    return '.'.join(q)

def ParseData(fileName):
    flow = []
    FORMAT = dict(t=3, IP_Port=5, protocol=6, flowSize=10, endT=4) # Defines the FORMAT of the data file
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line or line[0:10] != 'textexport':
            break
        if line == '\n': # Ignore Blank Line
            continue
        item = line.rsplit(' ')
        # print 'item Length: ' + str(len(item))
        f = dict()
        # print FORMAT
        for k, v in FORMAT.iteritems():
            if k == 'flowSize' or k == 't' or k == 'endT':
                f[k] = float(item[v])
            elif k == 'IP_Port':
                sd = item[v].rsplit('->')
                if len(sd) != 2:
                    raise ValueError('Format Incorrect')
                [srcIPStr, srcPortStr] = sd[0].rsplit(':')
                f['srcIPStr'] = srcIPStr
                f['srcIP'] = dottedQuadToNum(srcIPStr)
                f['srcPort'] = int(srcPortStr)
                IPDigit = srcIPStr.rsplit('.')
                f['srcIPVec'] = [int(IPDigit[0]), int(IPDigit[1]), int(IPDigit[2]), int(IPDigit[3]) ]

                [destIPStr, destPortStr] = sd[1].rsplit(':')
                f['destIPStr'] = destIPStr
                f['destIP'] = dottedQuadToNum(destIPStr)
                f['destPort'] = int(destPortStr)
                IPDigit = destIPStr.rsplit('.')
                f['destIPVec'] = [int(IPDigit[0]), int(IPDigit[1]), int(IPDigit[2]), int(IPDigit[3]) ]
            else:
                f[k] = item[v]

        # print f
        flow.append(f)

    fid.close()

    return flow

if __name__ == "__main__":
    ParseData('./data/data3a.txt')


