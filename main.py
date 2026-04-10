import asyncio
import re

from prompt_toolkit import print_formatted_text as print, PromptSession
from prompt_toolkit.formatted_text import FormattedText, StyleAndTextTuples
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.patch_stdout import patch_stdout

from core import fcore, CoreError, CoreShutdown, word
import preamble


class forth(fcore, Lexer):
    def __init__(self):
        super().__init__()
        self.w.append(preamble.words)
        self['style.prompt'] = ('> ',)
        self['style.float'] = ('#00bb00',)
        self['style.int'] = ('#44ff66',)
        self['style.text'] = ('#ffffff italic',)
        self['style.keyword'] = ('#3355ee',)
        self['style.error'] = ('#ff2222',)

    async def run(self):
        while True:
            try:
                await self.step()
            except CoreShutdown:
                break
            except CoreError as e:
                print(FormattedText([(self['style.error'][0], ''.join(e.args))]))


    async def get_input(self):
        session = PromptSession()
        with patch_stdout():
            while True:
                try:
                    user_input = await session.prompt_async(self['style.prompt'][0], lexer=self, vi_mode=True)
                except (EOFError, KeyboardInterrupt):
                    await self.put(word('bye'))
                    break
                await self.put(user_input)
                await self.put(word('eval'))
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

async def main():
    core = forth()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(core.get_input())
        tg.create_task(core.run())

if __name__ == "__main__":
    asyncio.run(main())
