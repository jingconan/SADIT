#!/usr/bin/env python
""" An simple script to export flow, for test use only
"""
from __future__ import print_function, division

from subprocess import check_call
def export_to_txt(f_name, txt_f_name):

    # cmd = """tshark -o column.format:'"No.", "%%m", "Time", "%%t", "Source", "%%s", "Destination", "%%d", "srcport", "%%uS", "dstport", "%%uD", "len", "%%L", "Protocol", "%%p"' -r %s > %s"""%(f_name, txt_f_name)

    cmd = """tshark -o column.format:'"No.", "%%m", "Time", "%%t", "Source", "%%s", "Destination", "%%d", "srcport", "%%uS", "dstport", "%%uD", "len", "%%L", "Protocol", "%%p"' -r %s > %s"""%(f_name, txt_f_name)

    # args = ['tshark', '-r', f_name, '>', txt_f_name]
    # cmd = ' '.join(args)
    print('--> ', cmd)
    check_call(cmd, shell=True)

def parse_txt(f_name):
    raw = lambda x:x
    dotted_int = lambda x: tuple(int(v) for v in x.rsplit('.'))
    FORMAT = dict(
            seq = (0, int),
            start_time = (1, float),
            src_ip = (2, str),
            dst_ip = (4, str),
            # src_ip = (2, dotted_int),
            # dst_ip = (4, dotted_int),
            src_port = (5, int),
            dst_port = (6, int),
            length = (7, float),
            protocol = (8, str),
            )

    NULL = lambda x: 0

    FORMAT_ARP = dict(
            seq = (0, int),
            start_time = (1, float),
            src_ip = (2, str),
            dst_ip = (4, str),
            length = (5, float),
            protocol = (6, str),
            src_port = (0, NULL), # FIXME
            dst_port = (0, NULL), # FIXME
            )



    fid = open(f_name, 'r')
    record = []
    while True:
        tline = fid.readline()
        if not tline:
            break
        if tline == '\n': # Ignore Blank Line
            continue
        item = tline.rsplit()
        try:
            f = [fmter(item[v]) for (v, fmter) in FORMAT.itervalues()]
        except IndexError as e:
            try:
                f = [fmter(item[v]) for (v, fmter) in FORMAT_ARP.itervalues()]
            except IndexError as e2:
                print('ignore packet, item: ', item)

        record.append(f)

    fid.close()
    return record, FORMAT.keys()

def change_to_flows(records, name, time_out):
    t_seq = name.index('start_time')
    length_seq = name.index('length')
    # five_tuple_seq = [name.index(k) for k in ['src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol']]
    five_tuple_seq = [name.index(k) for k in ['src_ip', 'dst_ip', 'protocol']]
    open_flows = dict()
    res_flow = []
    for rec in records:
        # five_tuple = get_five_tuple(rec)
        five_tuple = tuple(rec[seq] for seq in five_tuple_seq)
        t = rec[t_seq]
        length = rec[length_seq]
        # check time out
        remove_flows = []
        for f_tuple, (st_time, last_time, fs) in open_flows.iteritems():
            if t - last_time > time_out: # time out
                fd = t - st_time
                res_flow.append( (st_time, ) + f_tuple + (fs, fd))
                remove_flows.append(f_tuple)
        for f_tuple in remove_flows:
            del open_flows[f_tuple]

        stored_rec = open_flows.get(five_tuple, None)
        if stored_rec is not None: # if already exists
            (st_time_old, last_time_old, fs_old) = stored_rec
            open_flows[five_tuple] = (st_time_old, t, fs_old + length)
        else: # not exisit
            open_flows[five_tuple] = (t, t, length)

    print("""
Totoal Packets: [%i]
Exported Flows: [%i]
Open Flows: [%i]
            """%(len(records), len(res_flow), len(open_flows)))

    return res_flow

def write_flow(flows, f_name):
    fid = open(f_name, 'w')
    for f in flows:
        fid.write(' '.join([str(v) for v in f]) + '\n')
    fid.close()

def pcap2flow(pcap_file_name, flow_file_name, time_out):
    txt_f_name = pcap_file_name.rsplit('.pcap')[0] + '_tshark.txt'
    export_to_txt(pcap_file_name, txt_f_name)
    records, name = parse_txt(txt_f_name)
    res_flows = change_to_flows(records, name, time_out)
    write_flow(res_flows, flow_file_name)

import os
def loop_folder(folder_name, time_out):
    """is not quite sucessful right now"""
    import glob
    for pcap_file_name in glob.glob( os.path.join(folder_name, '*.pcap') ):
        print("--> start to process pcap_file_nam: [%s]"%(pcap_file_name))
        pcap2flow(
                pcap_file_name,
                pcap_file_name.rsplit('.pcap')[0] + '.flow',
                time_out
                )


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='pcap2netflow')
    parser.add_argument('-p', '--pcap', default=None,
            help='specify the pcap file you want to process')
    parser.add_argument('-f', '--folder', default=None,
            help='specify the folder you want to loop through')

    parser.add_argument('-t', '--time_out', default=10, type=float,
            help='time out time')

    args = parser.parse_args()

    if args.pcap:
        pcap2flow(args.pcap, args.pcap.rsplit('.pcap')[0] + '.flow', args.time_out)
    elif args.folder:
        loop_folder(args.folder, args.time_out)
    else:
        parser.print_help()



    # export_to_txt('./best_malware_protection.pcap')
    # records, name = parse_txt('./best_malware_protection_tshark.txt')
    # res_flows = change_to_flows(records, name, 0.1)
    # write_flow(res_flows, './best_malware_protection_tshark.flow')

