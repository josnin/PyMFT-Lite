from src.application import message_bus, handlers

def base_bootstrap(uow, storage_map, slack_adapter=None):
    """The 'Wiring' Logic"""
    
    # Inject dependencies into Command Handlers
    injected_command_handlers = {
        cmd_type: lambda cmd, h=handler: h(cmd, uow, storage_map)
        for cmd_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    # Inject dependencies into Event Handlers
    injected_event_handlers = {
        event_type: [
            lambda e, h=handler: h(e, slack_adapter) 
            for handler in handler_list
        ]
        for event_type, handler_list in handlers.EVENT_HANDLERS.items()
    }

    return message_bus.MessageBus(
        uow=uow,
        command_handlers=injected_command_handlers,
        event_handlers=injected_event_handlers
    )
