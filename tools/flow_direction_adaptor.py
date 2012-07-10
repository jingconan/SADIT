#!/usr/bin/env python
def switch(attr_list,  a, b):
    tmp = attr_list[a]
    attr_list[a] = attr_list[b]
    attr_list[b] = tmp
    return attr_list

def switch_C_S(attr_list):
    n = len(attr_list)
    CbIdx = [i for i in xrange(n) if attr_list[i].startswith('Cb=')]
    SbIdx = [i for i in xrange(n) if attr_list[i].startswith('Sb=')]
    assert(len(CbIdx)==1)
    assert(len(SbIdx)==1)
    switch(attr_list, CbIdx[0], SbIdx[0])

    # CpIdx = [i for i in xrange(n) if attr_list[i].startswith('Cp=')]
    # SpIdx = [i for i in xrange(n) if attr_list[i].startswith('Sp=')]
    # assert(len(CpIdx)==1)
    # assert(len(SpIdx)==1)
    # switch(attr_list, CpIdx[0], SpIdx[0])

    address = [i for i in xrange(n) if len(attr_list[i].rsplit('.')) == 4 ]
    assert( len(address) == 2 )
    switch(attr_list, address[0], address[1])

    return attr_list

def flow_direction_adaptor(fname, out_fname):
    fid = open(fname, 'r')
    fid_out = open(out_fname, 'w')
    while True:
        line = fid.readline()
        if not line: break
        attr_list = line.split(' ')
        # import pdb;pdb.set_trace()
        n = len(attr_list)

        if '->' in attr_list:
            # fid_out.write(' '.join(attr_list) + '\n')
            fid_out.write(' '.join(attr_list))
            continue
        elif '<-' in attr_list:
            attr_list = switch_C_S(attr_list)
            markIdx = [i for i in xrange(n) if attr_list[i] == '<>' or attr_list[i] == '<-']
            attr_list[markIdx[0]] = '->'
            # fid_out.write(' '.join(attr_list) + '\n')
            fid_out.write(' '.join(attr_list))
        elif '<>' in attr_list:
            markIdx = [i for i in xrange(n) if attr_list[i] == '<>' or attr_list[i] == '<-']
            attr_list[markIdx[0]] = '->'
            # fid_out.write(' '.join(attr_list) + '\n')
            fid_out.write(' '.join(attr_list))
            attr_list = switch_C_S(attr_list)
            # fid_out.write(' '.join(attr_list) + '\n')
            fid_out.write(' '.join(attr_list))
        else:
            raise Exception('Unknown Format Error')
    fid.close()
    fid_out.close()

if __name__ == "__main__":
    flow_direction_adaptor('../../CyberData/back_20030902.07.flow.txt',
            '../../CyberData/20030902.07.flow.txt')
    flow_direction_adaptor('../../CyberData/back_20070501.18.flow.txt',
            '../../CyberData/20070501.18.flow.txt')
