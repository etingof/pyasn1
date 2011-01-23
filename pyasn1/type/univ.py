# ASN.1 "universal" data types
import string
import types
import operator
from pyasn1.type import base, tag, constraint, namedtype, namedval
from pyasn1 import error

# "Simple" ASN.1 types (yet incomplete)

class Integer(base.AbstractSimpleAsn1Item):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x02)
        )
    namedValues = namedval.NamedValues()
    def __init__(self, value=None, tagSet=None, subtypeSpec=None,
                 namedValues=None):
        if namedValues is None:
            self.__namedValues = self.namedValues
        else:
            self.__namedValues = namedValues
        base.AbstractSimpleAsn1Item.__init__(
            self, value, tagSet, subtypeSpec
            )

#XXX    def __coerce__(self, other): return long(self), long(other)
    def __and__(self, value): return self.clone(self._value & value)
    def __rand__(self, value): return self.clone(value & self._value)
    def __or__(self, value): return self.clone(self._value | value)
    def __ror__(self, value): return self.clone(value | self._value)
    def __xor__(self, value): return self.clone(self._value ^ value)
    def __rxor__(self, value): return self.clone(value ^ self._value)
    def __add__(self, value): return self.clone(self._value + value)
    def __radd__(self, value): return self.clone(value + self._value)
    def __sub__(self, value): return self.clone(self._value - value)
    def __rsub__(self, value): return self.clone(value - self._value)
    def __mul__(self, value): return self.clone(self._value * value)
    def __rmul__(self, value): return self.clone(value * self._value)
    def __div__(self, value):  return self.clone(self._value / value)
    def __rdiv__(self, value):  return self.clone(value / self._value)
    def __mod__(self, value): return self.clone(self._value % value)
    def __rmod__(self, value): return self.clone(value % self._value)
    def __pow__(self, value, modulo=None):
        return self.clone(pow(self._value, value, modulo))
    def __rpow__(self, value): return self.clone(pow(value, self._value))
    def __lshift__(self, value): return self.clone(self._value << value)
    def __rshift__(self, value): return self.clone(self._value >> value)
    def __int__(self): return int(self._value)
    def __long__(self): return long(self._value)
    def __float__(self): return float(self._value)    
    def __abs__(self): return abs(self._value)
    def __index__(self): return int(self._value)
    
    def prettyIn(self, value):
        if type(value) != types.StringType:
            return long(value)
        r = self.__namedValues.getValue(value)
        if r is not None:
            return r
        try:
            return string.atoi(value)
        except:
            try:
                return string.atol(value)
            except:
                raise error.PyAsn1Error(
                    'Can\'t coerce %s into integer' % value
                    )

    def prettyOut(self, value):
        r = self.__namedValues.getName(value)
        if r is not None:
            return '%s(%s)' % (r, value)
        else:
            return str(value)

    def getNamedValues(self): return self.__namedValues

    def clone(self, value=None, tagSet=None, subtypeSpec=None,
              namedValues=None):
        if value is None and tagSet is None and subtypeSpec is None \
               and namedValues is None:
            return self
        if value is None:
            value = self._value
        if tagSet is None:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        if namedValues is None:
            namedValues = self.__namedValues
        return self.__class__(value, tagSet, subtypeSpec, namedValues)

    def subtype(self, value=None, implicitTag=None, explicitTag=None,
                subtypeSpec=None, namedValues=None):
        if value is None:
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
        if namedValues is None:
            namedValues = self.__namedValues
        else:
            namedValues = namedValues + self.__namedValues
        return self.__class__(value, tagSet, subtypeSpec, namedValues)

class Boolean(Integer):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x01),
        )
    subtypeSpec = Integer.subtypeSpec+constraint.SingleValueConstraint(0,1)
    namedValues = Integer.namedValues.clone(('False', 0), ('True', 1))

class BitString(base.AbstractSimpleAsn1Item):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x03)
        )
    namedValues = namedval.NamedValues()
    def __init__(self, value=None, tagSet=None, subtypeSpec=None,
                 namedValues=None):
        if namedValues is None:
            self.__namedValues = self.namedValues
        else:
            self.__namedValues = namedValues
        base.AbstractSimpleAsn1Item.__init__(
            self, value, tagSet, subtypeSpec
            )

    def clone(self, value=None, tagSet=None, subtypeSpec=None,
              namedValues=None):
        if value is None and tagSet is None and subtypeSpec is None \
               and namedValues is None:
            return self
        if value is None:
            value = self._value
        if tagSet is None:
            tagSet = self._tagSet
        if subtypeSpec is None:
            subtypeSpec = self._subtypeSpec
        if namedValues is None:
            namedValues = self.__namedValues
        return self.__class__(value, tagSet, subtypeSpec, namedValues)

    def subtype(self, value=None, implicitTag=None, explicitTag=None,
                subtypeSpec=None, namedValues=None):
        if value is None:
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
        if namedValues is None:
            namedValues = self.__namedValues
        else:
            namedValues = namedValues + self.__namedValues
        return self.__class__(value, tagSet, subtypeSpec, namedValues)

    def __str__(self): return str(tuple(self))

    # Immutable sequence object protocol

    def __len__(self):
        if self._len is None:
            self._len = len(self._value)
        return self._len
    def __getitem__(self, i):
        if type(i) == types.SliceType:
            return self.clone(operator.getslice(self._value, i.start, i.stop))
        else:
            return self._value[i]
    def __add__(self, value): return self.clone(self._value + value)
    def __radd__(self, value): return self.clone(value + self._value)
    def __mul__(self, value): return self.clone(self._value * value)
    def __rmul__(self, value): return self.__mul__(value)

    def prettyIn(self, value):
        r = []
        if not value:
            return ()
        elif type(value) != types.StringType:
            return value
        elif value[0] == '\'':
            if value[-2:] == '\'B':
                for v in value[1:-2]:
                    r.append(int(v))
            elif value[-2:] == '\'H':
                for v in value[1:-2]:
                    i = 4
                    v = string.atoi(v, 16)
                    while i:
                        i = i - 1
                        r.append((v>>i)&0x01)
            else:
                raise error.PyAsn1Error(
                    'Bad bitstring value notation %s' % value
                    )                
        else:
            for i in string.split(value, ','):
                i = self.__namedValues.getValue(i)
                if i is None:
                    raise error.PyAsn1Error(
                        'Unknown identifier \'%s\'' % i
                        )
                if i >= len(r):
                    r.extend([0]*(i-len(r)+1))
                r[i] = 1
        return tuple(r)

    def prettyOut(self, value):
        return '\'%s\'B' % string.join(map(str, value), '')
        
class OctetString(base.AbstractSimpleAsn1Item):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x04)
        )
    def prettyOut(self, value): return str(value)
    def prettyIn(self, value): return str(value)
    
    # Immutable sequence object protocol
    
    def __len__(self):
        if self._len is None:
            self._len = len(self._value)
        return self._len
    def __getitem__(self, i):
        if type(i) == types.SliceType:
            return self.clone(operator.getslice(self._value, i.start, i.stop))
        else:
            return self._value[i]
    def __add__(self, value): return self.clone(self._value + value)
    def __radd__(self, value): return self.clone(value + self._value)
    def __mul__(self, value): return self.clone(self._value * value)
    def __rmul__(self, value): return self.__mul__(value)

class Null(OctetString):
    defaultValue = '' # This is tightly constrained
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x05)
        )
    subtypeSpec = OctetString.subtypeSpec+constraint.SingleValueConstraint('')
    
class ObjectIdentifier(base.AbstractSimpleAsn1Item):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x06)
        )
    def __add__(self, other): return self.clone(self._value + other)
    def __radd__(self, other): return self.clone(other + self._value)

    def asTuple(self): return self._value
    
    # Sequence object protocol
    
    def __len__(self):
        if self._len is None:
            self._len = len(self._value)
        return self._len
    def __getitem__(self, i):
        if type(i) == types.SliceType:
            return self.clone(
                operator.getslice(self._value, i.start, i.stop)
                )
        else:
            return self._value[i]

    def index(self, suboid): return self._value.index(suboid)

    def isPrefixOf(self, value):
        """Returns true if argument OID resides deeper in the OID tree"""
        l = len(self)
        if l <= len(value):
            if self._value[:l] == value[:l]:
                return 1
        return 0

    def prettyIn(self, value):
        """Dotted -> tuple of numerics OID converter"""
        if type(value) is types.TupleType:
            pass
        elif isinstance(value, ObjectIdentifier):
            return tuple(value)        
        elif type(value) is types.StringType:
            r = []
            for element in filter(None, string.split(value, '.')):
                try:
                    r.append(string.atoi(element, 0))
                except string.atoi_error:
                    try:
                        r.append(string.atol(element, 0))
                    except string.atol_error, why:                        
                        raise error.PyAsn1Error(
                            'Malformed Object ID %s at %s: %s' %
                            (str(value), self.__class__.__name__, why)
                            )
            value = tuple(r)

            pass
        else:
            value = tuple(value)

        for x in value:
            if x < 0:
                raise error.PyAsn1Error(
                    'Negative sub-ID in %s at %s' % (value, self.__class__.__name__)
                    )
    
        return value

    def prettyOut(self, value):
        """Tuple of numerics -> dotted string OID converter"""
        r = []
        for subOid in value:
            r.append(str(subOid))
            if r[-1] and r[-1][-1] == 'L':
                r[-1][-1] = r[-1][:-1]
        return string.join(r, '.')

class Real(base.AbstractSimpleAsn1Item):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x09)
        )

class Enumerated(Integer):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 0x0A)
        )

# "Structured" ASN.1 types

class SetOf(base.AbstractConstructedAsn1Item):
    componentType = None
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 0x11)
        )    

    def _cloneComponentValues(self, myClone, cloneValueFlag):
        idx = 0; l = len(self._componentValues)
        while idx < l:
            c = self._componentValues[idx]
            if c is not None:
                if isinstance(c, base.AbstractConstructedAsn1Item):
                    myClone.setComponentByPosition(
                        idx, c.clone(cloneValueFlag=cloneValueFlag)
                        )
                else:
                    myClone.setComponentByPosition(idx, c.clone())
            idx = idx + 1
        
    def _verifyComponent(self, idx, value):
        if self._componentType is not None and \
               not self._componentType.isSuperTypeOf(value):
            raise error.PyAsn1Error('Component type error %s' % value)

    def getComponentByPosition(self, idx): return self._componentValues[idx]
    def setComponentByPosition(self, idx, value=None, verifyConstraints=True):
        l = len(self._componentValues)
        if idx >= l:
            self._componentValues = self._componentValues + (idx-l+1)*[None]
        if value is None:
            if self._componentValues[idx] is None:
                if self._componentType is None:
                    raise error.PyAsn1Error('Component type not defined')
                self._componentValues[idx] = self._componentType.clone()
                self._componentValuesSet = self._componentValuesSet + 1
            return self
        elif type(value) != types.InstanceType:
            if self._componentType is None:
                raise error.PyAsn1Error('Component type not defined')
            if isinstance(self._componentType, base.AbstractSimpleAsn1Item):
                value = self._componentType.clone(value=value)
            else:
                raise error.PyAsn1Error('Instance value required')
        if verifyConstraints:
            if self._componentType is not None:
                self._verifyComponent(idx, value)
            self._verifySubtypeSpec(value, idx)            
        if self._componentValues[idx] is None:
            self._componentValuesSet = self._componentValuesSet + 1
        self._componentValues[idx] = value
        return self

    def getComponentTypeMap(self):
        if self._componentType is not None:
            return self._componentType.getTypeMap()

    def prettyPrint(self, scope=0):
        scope = scope + 1
        r = self.__class__.__name__ + ':\n'        
        for idx in range(len(self._componentValues)):
            r = r + ' '*scope + self._componentValues[idx].prettyPrint(scope)
        return r

class SequenceOf(SetOf):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 0x10)
        )

class SequenceAndSetBase(base.AbstractConstructedAsn1Item):
    componentType = namedtype.NamedTypes()
    def _cloneComponentValues(self, myClone, cloneValueFlag):
        idx = 0; l = len(self._componentValues)
        while idx < l:
            c = self._componentValues[idx]
            if c is not None:
                if isinstance(c, base.AbstractConstructedAsn1Item):
                    myClone.setComponentByPosition(
                        idx, c.clone(cloneValueFlag=cloneValueFlag)
                        )
                else:
                    myClone.setComponentByPosition(idx, c.clone())
            idx = idx + 1

    def _verifyComponent(self, idx, value):
        if idx >= self._componentTypeLen:
            raise error.PyAsn1Error(
                'Component type error out of range'
                )
        t = self._componentType[idx].getType()
        if not t.isSuperTypeOf(value):
            raise error.PyAsn1Error('Component type error %s vs %s' %
                                    (repr(t), repr(value)))

    def getComponentByName(self, name):
        return self.getComponentByPosition(
            self._componentType.getPositionByName(name)
            )
    def setComponentByName(self, name, value=None, verifyConstraints=True):
        return self.setComponentByPosition(
            self._componentType.getPositionByName(name), value,
            verifyConstraints
            )

    def getComponentByPosition(self, idx):
        try:
            return self._componentValues[idx]
        except IndexError:
            if idx < self._componentTypeLen:
                return
            raise
    def setComponentByPosition(self, idx, value=None, verifyConstraints=True):
        l = len(self._componentValues)
        if idx >= l:
            self._componentValues = self._componentValues + (idx-l+1)*[None]
        if value is None:
            if self._componentValues[idx] is None:
                self._componentValues[idx] = self._componentType.getTypeByPosition(idx).clone()
                self._componentValuesSet = self._componentValuesSet + 1
            return self
        elif type(value) != types.InstanceType:
            t = self._componentType.getTypeByPosition(idx)
            if isinstance(t, base.AbstractSimpleAsn1Item):
                value = t.clone(value=value)
            else:
                raise error.PyAsn1Error('Instance value required')
        if verifyConstraints:
            if self._componentTypeLen:
                self._verifyComponent(idx, value)
            self._verifySubtypeSpec(value, idx)            
        if self._componentValues[idx] is None:
            self._componentValuesSet = self._componentValuesSet + 1
        self._componentValues[idx] = value
        return self

    def getDefaultComponentByPosition(self, idx):
        if self._componentTypeLen and self._componentType[idx].isDefaulted:
            return self._componentType[idx].getType()

    def getComponentType(self):
        if self._componentTypeLen:
            return self._componentType
    
    def setDefaultComponents(self):
        if self._componentTypeLen == self._componentValuesSet:
            return
        idx = self._componentTypeLen
        while idx:
            idx = idx - 1
            if self._componentType[idx].isDefaulted:
                if self.getComponentByPosition(idx) is None:
                    self.setComponentByPosition(idx)
            elif not self._componentType[idx].isOptional:
                if self.getComponentByPosition(idx) is None:
                    raise error.PyAsn1Error(
                        'Uninitialized component #%s at %s' % (idx, repr(self))
                        )

    def prettyPrint(self, scope=0):
        scope = scope+1
        r = self.__class__.__name__ + ':\n'
        for idx in range(len(self._componentValues)):
            if self._componentValues[idx] is not None:
                r = r + ' '*scope
                componentType = self.getComponentType()
                if componentType is None:
                    r = r + '??'
                else:
                    r = r + componentType.getNameByPosition(idx)
                r = '%s=%s\n' % (
                    r, self._componentValues[idx].prettyPrint(scope)
                    )
        return r

class Sequence(SequenceAndSetBase):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 0x10)
        )

    def getComponentTypeMapNearPosition(self, idx):
        return self._componentType.getTypeMapNearPosition(idx)
    
    def getComponentPositionNearType(self, tagSet, idx):
        return self._componentType.getPositionNearType(tagSet, idx)
    
class Set(SequenceAndSetBase):
    tagSet = tag.initTagSet(
        tag.Tag(tag.tagClassUniversal, tag.tagFormatConstructed, 0x11)
        )

    def getComponent(self, innerFlag=0): return self
    
    def getComponentByType(self, tagSet, innerFlag=0):
        c = self.getComponentByPosition(
            self._componentType.getPositionByType(tagSet)
            )
        if innerFlag and isinstance(c, Set):
            # get inner component by inner tagSet
            return c.getComponent(1)
        else:
            # get outer component by inner tagSet
            return c
        
    def setComponentByType(self, tagSet, value=None, innerFlag=0,
                           verifyConstraints=True):
        idx = self._componentType.getPositionByType(tagSet)
        t = self._componentType.getTypeByPosition(idx)
        if innerFlag:  # set inner component by inner tagSet
            if t.getTagSet():
                self.setComponentByPosition(idx, value, verifyConstraints)
            else:
                t = self.setComponentByPosition(idx).getComponentByPosition(idx)
                t.setComponentByType(
                    tagSet, value, innerFlag, verifyConstraints
                    )
        else:  # set outer component by inner tagSet
            self.setComponentByPosition(idx, value, verifyConstraints)
            
    def getComponentTypeMap(self): return self._componentType.getTypeMap(1)

    def getComponentPositionByType(self, tagSet):
        return self._componentType.getPositionByType(tagSet)

class Choice(Set):
    tagSet = tag.TagSet()  # untagged
    sizeSpec = constraint.ConstraintsIntersection(
        constraint.ValueSizeConstraint(1, 1)
        )
    _currentIdx = None

    def __cmp__(self, other):
        if self._componentValues:
            return cmp(self._componentValues[self._currentIdx], other)
        return -1

    def verifySizeSpec(self):
        if self._currentIdx is None:
            raise error.PyAsn1Error('Component not chosen')
        else:
            self._sizeSpec(' ')

    def _cloneComponentValues(self, myClone, cloneValueFlag):
        try:
            c = self.getComponent()
        except error.PyAsn1Error:
            pass
        else:
            if isinstance(c, Choice):
                tagSet = c.getEffectiveTagSet()
            else:
                tagSet = c.getTagSet()
            if isinstance(c, base.AbstractConstructedAsn1Item):
                myClone.setComponentByType(
                    tagSet, c.clone(cloneValueFlag=cloneValueFlag)
                    )
            else:
                myClone.setComponentByType(tagSet, c.clone())

    def setComponentByPosition(self, idx, value=None, verifyConstraints=True):
        l = len(self._componentValues)
        if idx >= l:
            self._componentValues = self._componentValues + (idx-l+1)*[None]
        if self._currentIdx is not None:
            self._componentValues[self._currentIdx] = None
        if value is None:
            if self._componentValues[idx] is None:
                self._componentValues[idx] = self._componentType.getTypeByPosition(idx).clone()
                self._componentValuesSet = 1
                self._currentIdx = idx
            return self
        elif type(value) != types.InstanceType:
            value = self._componentType.getTypeByPosition(idx).clone(
                value=value
                )
        if verifyConstraints:
            if self._componentTypeLen:
                self._verifyComponent(idx, value)
            self._verifySubtypeSpec(value, idx)            
        self._componentValues[idx] = value
        self._currentIdx = idx
        self._componentValuesSet = 1
        return self

    def getMinTagSet(self):
        if self._tagSet:
            return self._tagSet
        else:
            return self._componentType.genMinTagSet()

    def getEffectiveTagSet(self):
        if self._tagSet:
            return self._tagSet
        else:
            c = self.getComponent()
            if isinstance(c, Choice):
                return c.getEffectiveTagSet()
            else:
                return c.getTagSet()

    def getTypeMap(self):
        if self._tagSet:
            return Set.getTypeMap(self)
        else:
            return Set.getComponentTypeMap(self)

    def getComponent(self, innerFlag=0):
        if self._currentIdx is None:
            raise error.PyAsn1Error('Component not chosen')
        else:
            c = self._componentValues[self._currentIdx]
            if innerFlag and isinstance(c, Choice):
                return c.getComponent(innerFlag)
            else:
                return c

    def getName(self, innerFlag=0):
        if self._currentIdx is None:
            raise error.PyAsn1Error('Component not chosen')
        else:
            if innerFlag:
                c = self._componentValues[self._currentIdx]
                if isinstance(c, Choice):
                    return c.getName(innerFlag)
            return self._componentType.getNameByPosition(self._currentIdx)

    def setDefaultComponents(self): pass

# XXX
# coercion rules?
