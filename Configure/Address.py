from __future__ import print_function, division, absolute_import
def IntToDottedIP( intip ):
    """  Change a large integer to a dotted IP

    Parameters
    ---------------
    intip : int
        int representation of ip address

    Returns
    --------------
    res : str
        dotted string.

    Examples
    ---------------
    >>> IntToDottedIP(256)
    '0.0.1.0'

    """
    octet = ''
    for exp in [3,2,1,0]:
            octet = octet + str(intip // ( 256 ** exp )) + "."
            intip = intip % ( 256 ** exp )
    return(octet.rstrip('.'))

def DottedIPToInt( dotted_ip ):
    """  change dotted ip string intro a integer

    Parameters
    ---------------
    dotted_ip : str
        string with dotted seperated number

    Returns
    --------------
    res : int
        int representation of the IP address

    Examples
    ---------------
    >>> DottedIPToInt('0.0.1.0')
    256

    """
    exp = 3
    intip = 0
    for quad in dotted_ip.split('.'):
            intip = intip + (int(quad) * (256 ** exp))
            exp = exp - 1
    return(intip)

class Ipv4AddressHelper(object):
    """ Manage and Allocate Ipv4Address. Replica of Ipv4AddressHelper in NS3.

    Parameters
    -----------------
    network, mast, address : str consists of four dot seperated ints
        `network` is the network address. `mask` is the mask address
        `address` is the base address ( the first address that will be
        assigned for each network).

    Attributes
    -----------------
    m_shift : int
        the number of trailing zeros in the *network mask*.
    m_max : int
        the maximum number that is allowed for current network mask. The size
        of the subnet
    m_network, m_mask, m_base, m_address : int
        int representation of *network address*, *mask address*, *base address*
        and the next address that will be allocated.

    Examples
    -----------------------------
    >>> network = '10.0.7.0'
    >>> mask = '255.255.255.0'
    >>> base = '0.0.0.4'
    >>> helper = Ipv4AddressHelper(network, mask, base)
    >>> # helper.SetBase()
    >>> addr = helper.NewAddress()
    >>> print(addr)
    10.0.7.4
    >>> helper.NewNetwork()
    >>> addr = helper.NewAddress()
    >>> print(addr)
    10.0.8.4

    """
    def __init__(self, network, mask, address):
        self.SetBase(network, mask, address)

    def SetBase(self, network, mask, base):
        """ Set the `network`, `mask` and `base`

        Parameters
        ---------------
        network, mask, base: str of dotted ints
            the str represetation of `network`, `mask` and `base` addresses.

        Returns
        --------------
        None

        """
        self.m_network = DottedIPToInt(network)
        self.m_mask = DottedIPToInt(mask)
        self.m_base = DottedIPToInt(base)
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
        """ Create a new network.

        """
        self.m_network += 1
        self.m_address = self.m_base
        # IntToDottedIP( self.m_network << self.m_shift)

    def NewAddress(self):
        """ Get a new address from the current network.

        Notes
        --------------
        The way this is expected to be used is that an address and network
        number are initialized, and then NewAddress() is called repeatedly to
        allocate and get new addresses on a given subnet.  The client will
        expect that the first address she gets back is the one she used to
        initialize the generator with.  This implies that this operation is a
        post-increment.

        """
        assert(self.m_address < self.m_max)
        addr = IntToDottedIP((self.m_network << self.m_shift) | self.m_address);
        self.m_address += 1
        return addr

    def Assign(self, node_container):
        """ Assign addresses to node_container.

        Parameters
        ------------------
        node_container : list of node
            list of node that will be assigned address.

        Returns
        -------------------
        None

        Notes
        ----------------------
        each node will be added a interface in the same network

        """
        for node in node_container:
            node.add_interface_addr(self.NewAddress() + '/' + str(32-self.m_shift))

    def NumAddressBits(self, maskbits):
        """ Get number of trailing zeros in network mask

        Parameters
        ---------------
        maskbits : int
            int representation of nework `mask`.

        Returns
        --------------
        res : int
            number of trailing zeros

        Examples
        ---------------
        >>> network = '10.1.0.0'
        >>> mask = '255.255.0.0'
        >>> base = '0.0.0.4'
        >>> addrHelper = Ipv4AddressHelper(network, mask, base)
        >>> int_mask = DottedIPToInt(mask)
        >>> maskbits = addrHelper.NumAddressBits(int_mask)
        >>> print(maskbits)
        16
        >>> network = '10.0.7.0'
        >>> mask = '255.255.255.0'
        >>> addrHelper.SetBase(network, mask, base)
        >>> maskbits = addrHelper.NumAddressBits(DottedIPToInt(mask))
        >>> print(maskbits)
        8

        """
        for i in xrange(32):
            if (maskbits & 1):
                return i
            maskbits >>= 1;
        raise Exception("Ipv4AddressHelper::NumAddressBits():Bad Mask")
        return 0;

if __name__ == "__main__":
    import doctest
    doctest.testmod()
