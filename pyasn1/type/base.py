# Base classes for ASN.1 types
try:
    from sys import version_info
except ImportError:
    version_info = (0, 0)   # a really early version
from operator import getslice, setslice, delslice
from string import join
from types import SliceType
from pyasn1.type import constraint
from pyasn1 import error

class Asn1Item: pass

class Asn1ItemBase(Asn1Item):
    # Set of tags for this ASN.1 type
    tagSet = ()
    
    # A list of constraint.Constraint instances for checking values
    subtypeSpec = constraint.ConstraintsIntersection()

    def __init__(self, tagSet=None, subtypeSpec=None):
        if tagSet is None:
            self._tagSet = self.tagSet
        else:
            self._tagSet = tagSet
        if subtypeSpec is None:
            self._subtypeSpec = self.subtypeSpec
        else:
            self._subtypeSpec = subtypeSpec
        
    def _verifySubtypeSpec(self, value, idx=None):
        self._subtypeSpec(value, idx)
        
    def getSubtypeSpec(self): return self._subtypeSpec
    
    def getTagSet(self): return self._tagSet
    def getTypeMap(self): return { self._tagSet: self }
    
    def isSameTypeWith(self, other):
        return self is other or \
               self._tagSet == other.getTagSet() and \
               self._subtypeSpec == other.getSubtypeSpec()
    def isSuperTypeOf(self, other):
        """Returns true if argument is a ASN1 subtype of ourselves"""
        return self._tagSet.isSuperTagSetOf(other.getTagSet()) and \
               self._subtypeSpec.isSuperTypeOf(other.getSubtypeSpec())

# Base class for "simple" ASN.1 objects. These are immutable.
class AbstractSimpleAsn1Item(Asn1ItemBase):    
    defaultValue = None
    def __init__(self, value=None, tagSet=None, subtypeSpec=None):
        Asn1ItemBase.__init__(self, tagSet, subtypeSpec)
        if value is None:
            self._value = self.defaultValue
        else:
            value = self.prettyIn(value)
            self._verifySubtypeSpec(value)
            self._value = value
        self.__hashedValue = hash(self._value)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(
            self.prettyOut(self._value)
            ) +')'
    def __str__(self): return str(self._value)
    def __cmp__(self, value): return cmp(self._value, value)
    def __hash__(self): return self.__hashedValue

    def __nonzero__(self):
        if self._value: return 1
        else: return 0

    def clone(self, value=None, tagSet=None, subtypeSpec=None,
              cloneValueFlag=None):
        if value is None and tagSet is None and subtypeSpec is None:
            return self
        if cloneValueFlag:
            value = self._value
        if tagSet is None:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        return self.__class__(value, tagSet, subtypeSpec)

    def subtype(self, value=None, implicitTag=None, explicitTag=None,
                subtypeSpec=None, cloneValueFlag=None):
        if cloneValueFlag:
            value = self._value
        if implicitTag is not None:
            tagSet = self._tagSet.tagImplicitly(implicitTag)
        elif explicitTag is not None:
            tagSet = self._tagSet.tagExplicitly(explicitTag)
        else:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        else:
            subtypeSpec = subtypeSpec + self._subtypeSpec
        return self.__class__(value, tagSet, subtypeSpec)

    def prettyIn(self, value): return value
    def prettyOut(self, value): return str(value)

    def prettyPrint(self, scope=0): return self.prettyOut(self._value)
    # XXX Compatibility stub
    def prettyPrinter(self, scope=0): return self.prettyPrint(scope)
    
#
# Constructed types:
# * There are five of them: Sequence, SequenceOf/SetOf, Set and Choice
# * ASN1 types and values are represened by Python class instances
# * Value initialization is made for defaulted components only
# * Primary method of component addressing is by-position. Data model for base
#   type is Python sequence. Additional type-specific addressing methods
#   may be implemented for particular types.
# * SequenceOf and SetOf types do not implement any additional methods
# * Sequence, Set and Choice types also implement by-identifier addressing
# * Sequence, Set and Choice types also implement by-asn1-type (tag) addressing
# * Sequence and Set types may include optional and defaulted
#   components
# * Constructed types hold a reference to component types used for value
#   verification and ordering.
# * Component type is a scalar type for SequenceOf/SetOf types and a list
#   of types for Sequence/Set/Choice.
#

class AbstractConstructedAsn1Item(Asn1ItemBase):
    componentType = None
    sizeSpec = constraint.ConstraintsIntersection()
    def __init__(self, componentType=None, tagSet=None,
                 subtypeSpec=None, sizeSpec=None):
        Asn1ItemBase.__init__(self, tagSet, subtypeSpec)
        if componentType is None:
            self._componentType = self.componentType
        else:
            self._componentType = componentType
        if sizeSpec is None:
            self._sizeSpec = self.sizeSpec
        else:
            self._sizeSpec = sizeSpec
        self._componentValues = []

    def __repr__(self):
        r = self.__class__.__name__ + '()'
        for idx in range(len(self)):
            if self._componentValues[idx] is None:
                continue
            r = r + '.setComponentByPosition(%s, %s)' % (
                idx, repr(self._componentValues[idx])
                )
        return r

    def __cmp__(self, other): return cmp(self._componentValues, other)

    def getComponentTypeMap(self):
        raise error.PyAsn1Error('Method not implemented')

    def clone(self, tagSet=None, subtypeSpec=None, sizeSpec=None, 
              cloneValueFlag=None):
        if tagSet is None:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        if sizeSpec is None:
            sizeSpec = self._sizeSpec
        r = self.__class__(self._componentType, tagSet, subtypeSpec, sizeSpec)
        if cloneValueFlag:
            self._cloneComponentValues(r, cloneValueFlag)
        return r

    def subtype(self, implicitTag=None, explicitTag=None, subtypeSpec=None,
                sizeSpec=None, cloneValueFlag=None):
        if implicitTag is not None:
            tagSet = self._tagSet.tagImplicitly(implicitTag)
        elif explicitTag is not None:
            tagSet = self._tagSet.tagExplicitly(explicitTag)
        else:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        else:
            subtypeSpec = subtypeSpec + self._subtypeSpec
        if sizeSpec is None:
            sizeSpec = self._sizeSpec
        else:
            sizeSpec = sizeSpec + self._sizeSpec
        r = self.__class__(self._componentType, tagSet, subtypeSpec, sizeSpec)
        if cloneValueFlag:
            self._cloneComponentValues(r, cloneValueFlag)
        return r

    def _verifyComponent(self, idx, value): pass

    def verifySizeSpec(self): self._sizeSpec(self)

    def getComponentByPosition(self, idx):
        raise error.PyAsn1Error('Method not implemented')
    def setComponentByPosition(self, idx, value):
        raise error.PyAsn1Error('Method not implemented')

    def getComponentType(self): return self._componentType

    def __getitem__(self, idx): return self._componentValues[idx]

    def __len__(self): return len(self._componentValues)
    
    def clear(self): self._componentValues = []
