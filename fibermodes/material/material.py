'''
Created on 2014-05-01

@author: cbrunet
'''


class Material(object):

    '''
    classdocs
    '''

    name = "Abstract Material"
    nparams = 0

    @classmethod
    def n(cls, wl, *args, **kwargs):
        raise NotImplementedError(
            "This method must be implemented in super class.")

    @classmethod
    def info(cls):
        raise NotImplementedError(
            "This method must be implemented in super class.")

    @classmethod
    def __str__(cls):
        return cls.name

    @classmethod
    def __repr__(cls):
        return "{}()".format(cls.__name__)


if __name__ == '__main__':
    m = Material()
    print(m)
    print(repr(m))
