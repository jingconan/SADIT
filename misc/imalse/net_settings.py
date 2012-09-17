ipv4_net_addr_base = '10.7.0.1/24'
link_attr_default = ['2ms','5Mbps']
link_to_ip_map = {
    (0, 2):['', '10.20.30.5'],
    (0, 3):['', '10.20.30.2'],
    (0, 4):['', '10.20.30.3'],
    (0, 5):['', '10.20.30.4'],
    (1, 0):['10.200.1.1', ''],
    (6, 0):['10.1.1.1', '10.20.30.1'],
    (7, 6):['1.1.1.1', '60.70.80.1'],
}
# link_attr = {
# }
pcap_nodes = [  ]
pcap_links = [ (0,5) ]
botmaster_id_set = [ 5 ]
client_id_set = [ 2, 3, 4 ]
server_id_set = [ 0 ]
server_addr = [  ]
