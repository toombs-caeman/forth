from dataclasses import dataclass, field

def tokens(f:'Forth'):
    tok = f.s.pop().split(' ')
    f.s.extend(tok)
    f.s.append(len(tok))

def eval(f:'Forth'):
    count = f.s.pop()
    # equivalent
    #while count: f.i.append(f.s.pop()); count -= 1
    f.i.extend(reversed(f.s[-count:]))
    del f.s[-count:]

@dataclass
class Forth:
    # value stack
    s:list = field(default_factory=list)
    # instruction stack
    i:list = field(default_factory=lambda:['repl'])
    # heap
    #h:dict = field(default_factory=lambda:{'prompt':'> '})
    # words
    w:dict = field(default_factory=lambda:{
        '+':   lambda f:f.s.append(f.s.pop()+f.s.pop()),
        '-':   lambda f:f.s.append(-(f.s.pop()-f.s.pop())),
        '*':   lambda f:f.s.append(f.s.pop()*f.s.pop()),
        '/':   lambda f:f.s.append((f.s.pop()/f.s.pop())**-1),
        '.':   lambda f:print(f.s),
        's.':  lambda f:print(f.s.pop()),
        'dup': lambda f:f.s.append(f.s[-1]),
        'over':lambda f:f.s.append(f.s[-2]),
        'drop':lambda f:f.s.pop(),
        'swap':lambda f:f.s.append(f.s.pop(-2)),
        'rot-':lambda f:f.s.append(f.s.pop(-3)),
        #'rot':lambda f.s:f.s.append(f.s.pop(-3)),
        'depth':lambda f:f.s.append(len(f.s)),
        #'forth_repl':('forth_prompt', 'forth_getwords', 'forth_repl'),
        'repl':('prompt', 'read', 'tokens', 'eval', 'repl'),
        'prompt':lambda f:print('> ', end=''),
        'read':lambda f:f.s.append(input()),
        'tokens':tokens,
        'eval':eval,
        'bye':lambda f:f.i.clear(),
    })
    imm: bool = True

    def __call__(self):
        while self.i:
            t = self.i.pop()
            if t.isdecimal():
                self.s.append(int(t))
                continue
            if t.replace('.','', 1).isdecimal():
                self.s.append(float(t))
                continue
            fn = self.w[t]
            if callable(fn):
                fn(self) # fn is a base word
            else:
                self.i.extend(reversed(fn)) # fn is a composite word


if __name__ == "__main__":
    try:
        Forth()()
    except (EOFError,KeyboardInterrupt):
        pass
