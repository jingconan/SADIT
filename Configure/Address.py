def IntToDottedIP( intip ):
        octet = ''
        for exp in [3,2,1,0]:
                octet = octet + str(intip / ( 256 ** exp )) + "."
                intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))

def DottedIPToInt( dotted_ip ):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)

class Ipv4AddressHelper(object):
    """replica of Ipv4AddressHelper in NS3"""
    def __init__(self, network, mask, address):
        self.SetBase(network, mask, address)

    def SetBase(self, network, mask, address):
        self.m_network = DottedIPToInt(network)
        self.m_mask = DottedIPToInt(mask)
        self.m_base = DottedIPToInt(address)
        self.m_address = self.m_base

        assert( ( self.m_network & ~self.m_mask) == 0 )

        # Figure out how much to shift network numbers to get them
        # aligned, and what the maximum allowed address is with respect
        # to the current mask
        self.m_shift = self.NumAddressBits(self.m_mask)
        self.m_max = (1 << self.m_shift) - 2
        assert(self.m_shift <= 32)

        # shift the network down into the normalized position
        self.m_network >>= self.m_shift

    def NewNetwork(self):
        self.m_network += 1
        self.m_address = self.m_base
        IntToDottedIP( self.m_network << self.m_shift)

    def NewAddress(self):
        """The way this is expected to be used is that an address and network number
        are initialized, and then NewAddress() is called repeatedly to allocate and
        get new addresses on a given subnet.  The client will expect that the first
        address she gets back is the one she used to initialize the generator with.
        This implies that this operation is a post-increment.
        """
        assert(self.m_address < self.m_max)
        addr = IntToDottedIP((self.m_network << self.m_shift) | self.m_address);
        self.m_address += 1
        return addr

    def Assign(self, node_container):
        """node_container is a list of node that will be assigned address.
        each node will be added a interface same network
        """
        for node in node_container:
            node.add_interface_addr(self.NewAddress() + '/' + str(32-self.m_shift))

    def NumAddressBits(self, maskbits):
        for i in xrange(32):
            if (maskbits & 1):
                return i
            maskbits >>= 1;
        raise Exception("Ipv4AddressHelper::NumAddressBits():Bad Mask")
        return 0;

def test():
    network = '10.0.7.0'
    mask = '255.255.255.0'
    base = '0.0.0.4'
    helper = Ipv4AddressHelper(network, mask, base)
    # helper.SetBase()
    for i in xrange(10):
        helper.NewNetwork()
        addr = helper.NewAddress()
        print 'addr', addr

if __name__ == "__main__":
    test()
