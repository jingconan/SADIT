#!/usr/bin/env python
"""
Userd for debug
Check whether the flow in expected abnormal flow belongs to the total flow
"""

def load_content(f_name):
    fd = open(f_name, 'r')
    content = fd.readline().replace("\n", "")
    lines = []
    while (content != ""):
        content = fd.readline().replace("\n", "")
        lines.append(content)
    return lines


def check(f1, f2):
    lines_f1 = load_content(f1);
    print 'len f1', len(lines_f1)
    lines_f2 = load_content(f2);
    print 'len f2', len(lines_f2)
    i = 0
    # import pdb;pdb.set_trace()
    for l in lines_f1:
        i += 1
        if l.replace('abnormal_', '') not in lines_f2:
            print 'line, '
            print l
            print 'line no, ', i
            return False
    return True


if __name__ == "__main__":
    import sys
    print sys.argv
    print check(sys.argv[1], sys.argv[2])



