#!/usr/bin/env -S uv run pytest
import collections
from mod import definition
"""
* across the seven base units, correctly locking out unlike terms, and simplifying a value's degree
* aliases - preferred units for display
* conversions between units


* quantity
* dimensionality of that quantity across the seven physical axiis
* heirarchy of units
* conversion table between units
"""
def superize(i:int) -> str:
    "Turn an integer into unicode superscript."
    digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
    out = []
    if i == 0:
        return digits[0]
    neg = i < 0
    i = abs(i)
    while i:
        out.append(digits[i%10])
        i //= 10
    return ('⁻' if neg else '') + ''.join(reversed(out))

def test_superize():
    assert superize(-345) == '⁻³⁴⁵'
    assert superize(0) == '⁰'
    assert superize(1) == '¹'

vec7 = collections.namedtuple('_dim', ["time", "length", "mass", "current", "temperature", "amount", "luminosity",], defaults=[0] * 7)
metric_units = {
    # time
    's': 1,
    'min': 60,
    'h': 3600,
    'd': 24*3600,
    # length
    'm': 1,
    'cm': 0.01,
    'km': 1000,
    'au': 149597870700,
    # mass
    'kg': 1,
    'g': 0.001,
    'lb': 2.204623,
    # current
    "A": 1,
    # temperature
    # TODO this one is irregular
    # amount
    "mol": 1,
    # luminosity
    "cd": 1,

}

class Value:
    def __init__(self,
    quantity: float = 0,
    degree: vec7 = vec7(),
    scale: vec7 = vec7('s','m','kg','A','K', 'mol', 'cd'),
                 ):
        self.quantity = quantity
        self.degree = degree
        self.scale = scale

    def __validate_other(self, other, match=False) -> 'Value':
        """Raises an error if given an invalid"""
        match other:
            case Value():
                if match and self.degree != other.degree:
                    raise ValueError(f"attempting to operate on unlike dimensions. {self} != {other}")
                if self.scale != other.scale:
                    return other.rescale(self.scale)
                return other
            case int() | float():
                return Value(quantity=other)
            case _:
                raise ValueError()

    def __add__(self, other):
        other = self.__validate_other(other, True)
        return Value(quantity=self.quantity + other.quantity, degree=self.degree, scale=self.scale)
    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = self.__validate_other(other, True)
        return Value(quantity=self.quantity - other.quantity, degree=self.degree, scale=self.scale)

    def __mul__(self, other):
        other = self.__validate_other(other, False)
        return Value(quantity=self.quantity * other.quantity, degree=vec7(*(a+b for a,b in zip(self.degree, other.degree))), scale=self.scale)
    def __rmul__(self, other):
        return self * other

    def __pow__(self, other: int):
        return Value(quantity=self.quantity**other, degree=vec7(*(d*other for d in self.degree)), scale=self.scale)

    def __truediv__(self, other):
        other = self.__validate_other(other, False)
        return Value(quantity=self.quantity / other.quantity, degree=vec7(*(a-b for a,b in zip(self.degree, other.degree))), scale=self.scale)
    def __rtruediv__(self, other):
        other = self.__validate_other(other, False)
        return Value(quantity=other.quantity / self.quantity, degree=vec7(*(a-b for a,b in zip(other.degree, self.degree))), scale=self.scale)

    def rescale(self, scale: vec7 | str) -> 'Value':
        """convert the value to use a new scale."""
        # TODO make this able to change only a single dimension
        q = self.quantity
        for old, new, deg in zip(self.scale, scale, self.degree):
            if old != new:
                q *= (metric_units[new] / metric_units[old])**deg
        return Value(quantity=q, degree=self.degree, scale=scale)

    def __repr__(self):
        return f"{self.quantity} {'⋅'.join(
            sym if deg == 1 else f'{sym}{superize(deg)}'
            for deg, sym in zip(self.degree, self.scale)
            if deg
        )}"

unit = Value(quantity=1)
s    = Value(quantity=1, degree=vec7(1, 0, 0, 0, 0, 0, 0))
m    = Value(quantity=1, degree=vec7(0, 1, 0, 0, 0, 0, 0))
kg   = Value(quantity=1, degree=vec7(0, 0, 1, 0, 0, 0, 0))
A    = Value(quantity=1, degree=vec7(0, 0, 0, 1, 0, 0, 0))
K    = Value(quantity=1, degree=vec7(0, 0, 0, 0, 1, 0, 0))
mol  = Value(quantity=1, degree=vec7(0, 0, 0, 0, 0, 1, 0))
cd   = Value(quantity=1, degree=vec7(0, 0, 0, 0, 0, 0, 1))

ΔvCs = 9192631770 / s
def test_addsub():
    height = m + m
    assert height.degree == m.degree
    assert height.scale == m.scale
    assert height.quantity == 2
    height -= m
    assert height == m

def test_muldiv():
    assert (cd * cd).degree == vec7(0, 0, 0, 0, 0, 0, 2)
    assert (K / K).degree == unit.degree

words = definition()
for k,v in {'s':s, 'm':m, 'kg':kg, 'A':A, 'K':K, 'mol':mol, 'cd':cd,}.items():
    # TODO needs an extra closure
    words(k, lambda f:f.push(f.pop() * v))
    words('-'+k, lambda f:f.push(f.pop() / v))

