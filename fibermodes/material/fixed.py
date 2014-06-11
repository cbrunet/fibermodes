'''
Created on 2014-05-01

@author: cbrunet
'''

from .material import Material


class Fixed(Material):

    '''
    classdocs
    '''

    name = "Fixed index"
    nparams = 1

    @classmethod
    def n(cls, wl, n):
        return n

    @classmethod
    def info(cls):
        return "Fixed index"
