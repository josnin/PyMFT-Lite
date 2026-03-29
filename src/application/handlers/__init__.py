from src.application import commands
from .transfer import handle_transfer

COMMAND_HANDLERS = {
    # All these distinct business intents map to the same robust logic
    commands.ProcessInbound: handle_transfer,
    commands.SendToCustomer: handle_transfer,
    commands.CollectFromCustomer: handle_transfer,
}
