"""
async_event_manager - A more powerful way to fire callbacks and create decorator events with Cloudlink.

bind(func: <method>) 
* Adds an asyncio method to the event manager object.
* bind() should only be called during setup, and should not be called after the server is started.

unbind(func: <method>)
* Removes an asyncio method from the event manager object.
* unbind() should only be called during setup, and should not be called after the server is started.

reset()
* Clears all asyncio methods to be executed from the event manager object.
"""


class async_event_manager:
    def __init__(self, parent):
        # Declare constructor with initial state
        self.iterator = 0
        self.events = set()

        # Init logger
        self.logging = parent.logging
        self.logger = self.logging.getLogger(__name__)

    # Add functions to event list
    def bind(self, func):
        self.events.add(func)

    # Remove functions from events list
    def unbind(self, func):
        self.events.remove(func)

    # Cleanup events list
    def reset(self):
        self.iterator = 0
        self.events = set()

    # Create instance of async iterator
    def __aiter__(self):
        return self

    # Return next awaitable
    async def __anext__(self):
        # Check for further events in the list of events
        if self.iterator >= len(self.events):
            self.logger.debug(f"Finished executing awaitable events")
            self.iterator = 0
            raise StopAsyncIteration

        # Increment iterator
        self.iterator += 1

        # Execute async event
        self.logger.debug(f"Executing event {self.iterator} of {len(self.events)}")
        return list(self.events)[self.iterator - 1]
