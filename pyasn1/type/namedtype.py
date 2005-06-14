# NamedType specification for constructed types
from pyasn1 import error

class NamedType:
    isOptional = 0
    isDefaulted = 0
    def __init__(self, name, t):
        self.__name = name; self.__type = t
    def __repr__(self): return '%s(%s, %s)' % (
        self.__class__.__name__, repr(self.__name), repr(self.__type)
        )
    def getType(self): return self.__type
    def getName(self): return self.__name
    def __getitem__(self, idx):
        if idx == 0: return self.__name
        if idx == 1: return self.__type
        raise IndexError()
    
class OptionalNamedType(NamedType):
    isOptional = 1
class DefaultedNamedType(NamedType):
    isDefaulted = 1
    
class NamedTypes:
    def __init__(self, *namedTypes):
        self.__namedTypes = namedTypes
        self.__minTagSet = None
        self.__typeMap = {}; self.__tagMap = {}; self.__nameMap = {}
        self.__ambigiousTypes = {}

    def __repr__(self):
        r = '%s(' % self.__class__.__name__
        for n in self.__namedTypes:
            r = r + '%s, ' % repr(n)
        return r + ')'
    
    def __getitem__(self, idx): return self.__namedTypes[idx]

    def __nonzero__(self): return bool(self.__namedTypes)
    def __len__(self): return len(self.__namedTypes)
    
    def getTypeByPosition(self, idx):
        try:
            return self.__namedTypes[idx].getType()
        except IndexError:
            raise error.PyAsn1Error('Type position out of range')
    def getPositionByType(self, tagSet):
        if not self.__tagMap:
            idx = len(self.__namedTypes)
            while idx > 0:
                idx = idx - 1
                for t in self.__namedTypes[idx].getType().getTypeMap().keys():
                    if self.__tagMap.has_key(t):
                        raise error.PyAsn1Error('Duplicate type %s' % t)
                    self.__tagMap[t] = idx
        try:
            return self.__tagMap[tagSet]
        except KeyError:
            raise error.PyAsn1Error('Type %s not found' % tagSet)
        
    def getNameByPosition(self, idx):
        try:
            return self.__namedTypes[idx].getName()
        except IndexError:
            raise error.PyAsn1Error('Type position out of range')
    def getPositionByName(self, name):
        if not self.__nameMap:
            idx = len(self.__namedTypes)
            while idx > 0:
                idx = idx - 1
                n = self.__namedTypes[idx].getName()
                if self.__nameMap.has_key(n):
                    raise error.PyAsn1Error('Duplicate name %s' % n)
                self.__nameMap[n] = idx
        try:
            return self.__nameMap[name]
        except KeyError:
            raise error.PyAsn1Error('Name %s not found' % name)

    def __buildAmbigiousTagMap(self):
        ambigiousTypes = ()
        idx = len(self.__namedTypes)
        while idx > 0:
            idx = idx - 1
            t = self.__namedTypes[idx]
            if t.isOptional or t.isDefaulted:
                ambigiousTypes = (t, ) + ambigiousTypes
            else:
                ambigiousTypes = (t, )
            self.__ambigiousTypes[idx] = apply(NamedTypes, ambigiousTypes)
        
    def getTypeMapNearPosition(self, idx):
        if not self.__ambigiousTypes: self.__buildAmbigiousTagMap()
        try:
            return self.__ambigiousTypes[idx].getTypeMap()
        except KeyError:
            raise error.PyAsn1Error('Type position out of range')

    def getPositionNearType(self, tagSet, idx):
        if not self.__ambigiousTypes: self.__buildAmbigiousTagMap()
        try:
            return idx+self.__ambigiousTypes[idx].getPositionByType(tagSet)
        except KeyError:
            raise error.PyAsn1Error('Type position out of range')

    def genMinTagSet(self):
        if self.__minTagSet is None:
            for t in self.__namedTypes:
                __type = t.getType()
                tagSet = getattr(__type,'getMinTagSet',__type.getTagSet)()
                if self.__minTagSet is None or tagSet < self.__minTagSet:
                    self.__minTagSet = tagSet
        return self.__minTagSet
    
    def getTypeMap(self, uniq=None):
        if not self.__typeMap:
            for t in self.__namedTypes:
                __type = t.getType()
                typeMap = __type.getTypeMap()
                if uniq:
                    for k in typeMap.keys():
                        if self.__typeMap.has_key(k):
                            raise error.PyAsn1Error(
                               'Duplicate type %s in map %s'%(k,self.__typeMap)
                                )
                        self.__typeMap[k] = __type
                else:
                    for k in typeMap.keys():
                        self.__typeMap[k] = __type
        return self.__typeMap
