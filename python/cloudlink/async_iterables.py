"""
async_iterable - converts a list or set of methods into an asyncio iterable
which can be used in the async for function.

to use, init the class with the server parent and the list/set of functions.

import async_iterable
...
async for event in async_iterable(parent, [foo, bar]):
    await event()
"""


class async_iterable:
    def __init__(self, iterables):
        self.iterator = 0
        self.iterable = list(iterables)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.iterator >= len(self.iterable):
            self.iterator = 0
            raise StopAsyncIteration

        self.iterator += 1

        return self.iterable[self.iterator - 1]
