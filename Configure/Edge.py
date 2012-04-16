from pydot import *

class NEdge(Edge):
    def __init__(self, src, dst, attr):
        obj_dict = dict()
        obj_dict[ 'attributes' ] = attr
        obj_dict[ 'type' ] = 'edge'
        obj_dict[ 'parent_graph' ] = None
        obj_dict[ 'parent_edge_list' ] = None
        obj_dict[ 'sequence' ] = None
        if isinstance(src, Node):
            src = src.get_name()
        if isinstance(dst, Node):
            dst = dst.get_name()
        points = ( quote_if_necessary( src) , quote_if_necessary( dst) )
        obj_dict['points'] = points

        Edge.__init__(self, src, dst, obj_dict)
