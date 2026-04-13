import re
from collections.abc import Callable
import importlib
from ast import literal_eval

class CoreError(Exception):
    """core error."""

class CoreShutdown(Exception):
    """core is shutting down."""

class CoreAwaitInput(Exception):
    """core is stalled because it is waiting for input."""

class word(str):
    """a forth word."""

async def pyload(f):
    name = f.pop()
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        raise CoreError(f"module {name!r} not found.")

    words = getattr(module, 'words', None)
    if words is None:
        raise CoreError(f"module {module.__name__} contains no words")
    f.w.append(words)
    post = getattr(module, 'post', None)
    if post is not None:
        f.put(post)


class call:
    def __init__(self, *contents, name=None):
        self.name = name
        self.contents = contents
        self.idx = 0
    def __repr__(self) -> str:
        return f"{self.name or ''}{self.contents!r}"
    def __next__(self):
        if self.idx >= len(self.contents):
            raise StopIteration()
        x = self.contents[self.idx]
        self.idx += 1
        return x

class fcore:
    """
    a forth core, it should have no concept of IO niceties
    it defines no words
    it ingests a queue of values
    """
    # TODO move compiler to preamble
    tokenize = staticmethod(re.compile(r"""\s+|(\d+\.\d*)|(\d+)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\S+)""").finditer)
    cast = float, int, literal_eval, word
    @staticmethod
    def compile(src:str):
        # TODO raise CoreError on failure to consume input, mismatched quotes
        return (
            fcore.cast[m.lastindex-1](m[m.lastindex])
            for m in fcore.tokenize(src) if m.lastindex
        )

    def __init__(self, interactive=False):
        # definitions
        # TODO move scopes to a separate mod
        self.w:list[dict[str,tuple]] = [{
            'pyload':(pyload,),
            'style.prompt':('> ',),
        }]
        # data stack
        self.s = []
        # call stack
        self.c:list[call] = []
        self.interactive = interactive

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
    def __call__(self, word:word|str):
        """invoke a word"""
        name = str(word)
        self.put(*self[name], name=name)

    # get/put from instruction queue
    async def get(self):
        """get the next instruction off the call stack."""
        i = None
        while i is None:
            if not self.c:
                raise CoreAwaitInput()
            if (i := next(self.c[-1], None)) is None:
                self.c.pop()
        return i

    def put(self, *values, name=''):
        """add work to the call stack"""
        if not values:
            return
        self.c.append(call(*values, name=name))

    def pop(self, index=-1):
        """pop value from data stack"""
        try:
            return self.s.pop(index)
        except Exception:
            raise CoreError("stack underflow")
    def push(self, value):
        """push value to data stack"""
        self.s.append(value)

    async def step(self):
        """process then next instruction"""
        match (i := await self.get()):
            case word():
                self(i)
            case Callable():
                await i(self)
            case _:
                self.push(i)

    async def accept_input(self) -> bool:
        """accept input from the user. Return True if more input can be received"""
        try:
            src = input(''.join(self['style.prompt']))
        except (EOFError, KeyboardInterrupt):
            return False
        self.put(*self.compile(src), name='user')
        return True

    def handle_error(self, e):
        """handler for CoreError"""
        raise e

    async def run(self):
        """process instructions until shutdown received."""
        while True:
            try:
                await self.step()
            except CoreShutdown:
                break
            except CoreError as e:
                self.handle_error(e)
            except CoreAwaitInput:
                if not self.interactive or not await self.accept_input():
                    break

if __name__ == "__main__":
    import asyncio
    asyncio.run(fcore(interactive=True).run())
