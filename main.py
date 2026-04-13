import asyncio
from asyncio.queues import QueueShutDown
import re
from typing import Iterable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

from core import fcore, CoreError, CoreShutdown, word

from prompt_toolkit.formatted_text import FormattedText, StyleAndTextTuples
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.patch_stdout import patch_stdout



class forth(fcore, Lexer, Completer):
    def __init__(self):
        super().__init__(interactive=True)
        self['style.prompt'] = ('> ',)
        self['style.float'] = ('#00bb00',)
        self['style.int'] = ('#44ff66',)
        self['style.text'] = ('#ffffff italic',)
        self['style.keyword'] = ('#3355ee',)
        self['style.error'] = ('#ff2222',)
        self.put('mod.preamble', word('pyload'), name='core')
        self.q = asyncio.Queue()

    def handle_error(self, e):
        print(FormattedText([(self['style.error'][0], ''.join(e.args))]))

    async def run(self):
        with patch_stdout():
            async with asyncio.TaskGroup() as tg:
                prompt = tg.create_task(self.prompt())
                runner = tg.create_task(super().run())

    async def accept_input(self) -> bool:
        try:
            src = await self.q.get()
            self.put(*self.compile(src), name='user')
            self.q.task_done()
            return True
        except QueueShutDown:
            return False

    def get_completions(self, document: Document, complete_event:CompleteEvent) -> Iterable[Completion]:
        # TODO
        pass

    def toolbar(self):
        return 'hello'
        return FormattedText([('#ffffff', 'hello\nworld')])
        pass

    async def prompt(self):
        """Task for prompting the user for input"""
        kb = KeyBindings()
        # TODO F9 pause/continue
        # TODO F10 step over
        # TODO F11 step into
        # TODO F12 step out
        # TODO c-c/KeyboardInterrupt abort
        session = PromptSession(
            vi_mode=True,
            # TODO completer=self
            history=FileHistory('.hist.fth'),
            lexer=self,
            bottom_toolbar=self.toolbar,
            key_bindings=kb
        )
        #session.key_bindings.add()
        while True:
            try:
                await self.q.put(await session.prompt_async(self['style.prompt'][0]))
            except EOFError:
                self.q.shutdown()
                break

    lexer = re.compile(r"""(\d+\.\d*)|(\d+)|(\S+)|(\s+)""").finditer
    def lex(self, text):
        lexer_class = [self[k][0] for k in (
            'style.float',
            'style.int',
            'style.text',
            'style.text',
            'style.keyword',
        )]
        keyword = lexer_class[-1]
        for m in self.lexer(text):
            if m.lastindex is None:
                continue
            word = m[m.lastindex]
            if word in self:
                yield keyword, word
                continue
            yield lexer_class[m.lastindex-1], word
    def lex_document(self, document):
        def get_line(lineno) -> StyleAndTextTuples:
            return list(self.lex(document.lines[lineno]))
        return get_line

def churn(s:str):
    left, right = s.split(':')
    right = tuple(-1-int(d) for d in right)
    if not left:
        return lambda stack: stack.extend(stack[i] for i in right)

    left = -int(left)
    def _(stack):
        stack[left:] = (stack[i] for i in right)
    return _

if __name__ == "__main__":
    asyncio.run(forth().run())
