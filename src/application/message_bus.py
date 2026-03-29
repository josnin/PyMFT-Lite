from tenacity import retry, stop_after_attempt, wait_exponential

class MessageBus:
    def __init__(self, uow, command_handlers, event_handlers):
        self.uow = uow
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.queue = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def handle(self, message):
        self.queue = [message]
        while self.queue:
            msg = self.queue.pop(0)
            if hasattr(msg, "is_command"): 
                self._handle_command(msg)
            else:
                self._handle_event(msg)

    def _handle_command(self, cmd):
        handler = self.command_handlers[type(cmd)]
        handler(cmd)
        # Collect events generated during the command
        self.queue.extend(self.uow.collect_new_events())

    def _handle_event(self, event):
        for handler in self.event_handlers.get(type(event), []):
            handler(event)
