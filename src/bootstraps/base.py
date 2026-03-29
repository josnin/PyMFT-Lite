from src.application import message_bus, handlers
from src.domain import commands, events

def base_bootstrap(uow, cloud_adapter, onprem_adapter, slack_adapter=None):
    storage_map = {"aws": cloud_adapter, "onprem": onprem_adapter}

    command_handlers = {
        commands.ProcessInbound: lambda c: handlers.handle_inbound(c, uow, storage_map),
        commands.SendToCustomer: lambda c: handlers.handle_outbound(c, uow, storage_map),
    }

    event_handlers = {
        events.FileTransferred: [
            lambda e: handlers.log_completion(e),
            lambda e: handlers.notify_slack(e, slack_adapter) if slack_adapter else None,
        ]
    }

    return message_bus.MessageBus(uow, command_handlers, event_handlers)
