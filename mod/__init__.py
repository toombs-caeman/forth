import asyncio
import functools

class definition(dict):
    def __call__(self, name, f=None):
        """define a forth word"""
        # sort out a decorator call
        if callable(name):
            name, f = name.__name__, name
        if f is None:
            return lambda f:self(name, f)
        # ensure we're async
        if asyncio.iscoroutinefunction(f):
            final = f
        else:
            @functools.wraps(f)
            async def final(forth):
                return f(forth)
        self[name] = (final,)
        return final
