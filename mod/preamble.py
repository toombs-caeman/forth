"""
a forth preamble in python
"""
import asyncio
from core import CoreShutdown
from mod import definition

define = definition()

@define(':')
async def _(f):
    w = []
    while (x := await f.get()) != ';':
        w.append(x)
    f[w[0]] = tuple(w[-1:0:-1])

@define
def eval(f):
    f(reversed(tuple(f.compile(f.pop()))))

@define
def bye(f):
    raise CoreShutdown()

@define('?')
async def query(f):
    key = await f.get()
    if key in f:
        print(' '.join(str(v) for v in reversed(f[key])))


@define
def load(f):
    with open(f.pop(), 'r') as fd:
        f.push(fd.read())

@define
async def sleep(f):
    await asyncio.sleep(f.pop())

for k,v in {
        '+':   lambda f:f.push(f.pop()+f.pop()),
        '-':   lambda f:f.push(-(f.pop()-f.pop())),
        '*':   lambda f:f.push(f.pop()*f.pop()),
        '/':   lambda f:f.push((f.pop()/f.pop())**-1),
        '.':   lambda f:print(f.s),
        's.':  lambda f:print(f.s.pop()),
        'dup': lambda f:f.push(f.s[-1]),
        'over':lambda f:f.push(f.s[-2]),
        'drop':lambda f:f.pop(),
        'swap':lambda f:f.push(f.pop(-2)),
        'rot-':lambda f:f.push(f.pop(-3)),
        'depth':lambda f:f.push(len(f.s)),
}.items():
    define(k, v)
words = define
