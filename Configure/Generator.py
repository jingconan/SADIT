from __future__ import print_function, division, absolute_import
import copy
from string import Template

class Generator(object):
    def __init__(self, **para):
        self.para = para

    @property
    def template(self):
        # for backward compatibility
        if self.para['TYPE'] == 'harpoon':
            return Template('"harpoon ipsrc=$ipsrc '\
                   'ipdst=$ipdst '\
                   'flowsize=normal($flow_size_mean,$flow_size_var) '\
                   'flowstart=exponential($flow_arrival_rate) '\
                   'sport=randomchoice(22,80,443) '\
                   'dport=randomunifint(1025,65535) '\
                   'lossrate=randomchoice(0.001)"')

        return Template('"%s ipsrc=$ipsrc ipdst=$ipdst"' %(self.para['TYPE']))

    def __str__(self):
        return self.template.substitute(self.para)

    def get_new_gen(self, change_para=None):
        """  Generate a new generator accoding to `change_para`

        Parameters
        ---------------
        change_para : dict
            See `Anomaly` for the format of `change_para`

        Returns
        --------------
        new : generator class
            a new generator class

        """
        new = copy.deepcopy(self)
        if change_para is None:
            return new

        # change the parameters
        for attr, ratio in change_para.iteritems():
            name = attr.lower()
            try:
                orig_para = float(new.para[name])
            except KeyError as e:
                raise Exception("you are changing a parameter that doesn't"
                                " exist. Maybe wrong config file?")
            if isinstance(ratio, str):
                tp = ratio[0]
                r = ratio[1:]
                if tp == '=':
                    new.para[name] = '%s' % (r)
                elif tp == '+':
                    new.para[name] = '%f' % (orig_para + float(r))
                elif tp == 'x':
                    new.para[name] = '%f' % (orig_para * float(r))
                else:
                    raise Exception('unknown change parameter')

            # for backward compatibility
            elif isinstance(ratio, float) or isinstance(ratio, int):
                new.para[name] = '%f' % (orig_para * ratio)

        # new.sync()
        return new

def get_generator(gen_desc):
    """  generate generator
    """
    return Generator(**gen_desc)
