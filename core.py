import asyncio
import re
from collections import deque
from collections.abc import Callable

class CoreError(Exception):
    """a forth error."""

class CoreShutdown(Exception):
    """forth is gracefully shutting down."""

class word(str):
    """a forth word."""

type value = word | int | float | str | Callable

class fcore:
    """
    a forth core, it should have no concept of IO niceties
    it defines no words
    it ingests a queue of values
    """
    tokenize = staticmethod(re.compile(r"""\s+|(\d+\.\d*)|(\d+)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\S+)""").finditer)
    cast = float, int, str, word
    @staticmethod
    def compile(src:str):
        # TODO raise error on failure to consume input, mismatched quotes
        return (
            fcore.cast[m.lastindex-1](m[m.lastindex])
            for m in fcore.tokenize(src) if m.lastindex
        )
    def __init__(self):
        # definitions
        self.w:list[dict[str,tuple]] = [{}]
        # stack
        self.s = []
        # instruction queue
        self.i = deque()
        self.has_work = asyncio.Event()

    # get/set/contains words
    def __getitem__(self, key):
        for ns in reversed(self.w):
            if key in ns:
                return ns[key]
        raise CoreError(f"Unknown word: {key}")
    def __contains__(self, key):
        return any(key in ns for ns in self.w)

    def __setitem__(self, key, value:tuple):
        self.w[-1][key] = value

    # call word
    def __call__(self, work):
        self.i.extendleft(work)

    # get/put from instruction queue
    async def get(self):
        if not self.i:
            self.has_work.clear()
            await self.has_work.wait()
        return self.i.popleft()
    async def put(self, value):
        self.i.append(value)
        self.has_work.set()

    # push/pop from stack
    def pop(self, index=-1):
        try:
            return self.s.pop(index)
        except Exception:
            raise CoreError("stack underflow")
    def push(self, value):
        self.s.append(value)

    async def step(self):
        match (i := await self.get()):
            case word():
                self(self[i])
            case Callable():
                await i(self)
            case str() | int() | float():
                self.s.append(i)
            case _:
                raise CoreError(f"non-value of type {type(i)} in instruction stream.")

    async def run(self):
        while True:
            try:
                await self.step()
            except CoreShutdown:
                break
