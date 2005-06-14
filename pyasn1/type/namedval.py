# ASN.1 named integers
from  types import TupleType
from pyasn1 import error

__all__ = [ 'NamedValues' ]

class NamedValues:
    def __init__(self, *namedValues):
        self.nameToValIdx = {}; self.valToNameIdx = {}
        self.namedValues = ()        
        automaticVal = 1
        for namedValue in namedValues:
            if type(namedValue) == TupleType:
                name, val = namedValue
            else:
                name = namedValue
                val = automaticVal
            if self.nameToValIdx.has_key(name):
                raise error.PyAsn1Error('Duplicate name %s' % name)
            self.nameToValIdx[name] = val
            if self.valToNameIdx.has_key(val):
                raise error.PyAsn1Error('Duplicate value %s' % name)
            self.valToNameIdx[val] = name
            self.namedValues = self.namedValues + ((name, val),)
            automaticVal = automaticVal + 1
    def __str__(self): return str(self.namedValues)
    
    def getName(self, value): return self.valToNameIdx.get(value)
    def getValue(self, name): return self.nameToValIdx.get(name)
    
    def __getitem__(self, i): return self.namedValues[i]
    def __len__(self): return len(self.namedValues)

    def __add__(self, namedValues):
        return apply(self.__class__, self.namedValues + namedValues)
    def __radd__(self, namedValues):
        return apply(self.__class__, namedValues + tuple(self))
        
    def clone(self, *namedValues):
        return apply(self.__class__, tuple(self) + namedValues)

# XXX clone/subtype?
