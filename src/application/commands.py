from dataclasses import dataclass

@dataclass(frozen=True)
class TransferCommand:
    src_path: str
    dest_path: str
    src_provider: str
    dest_provider: str
    is_command: bool = True

    @property
    def file_name(self):
        return self.src_path.split('/')[-1]

# Specialized Commands (Inherit logic but represent specific business intents)
class ProcessInbound(TransferCommand): pass
class SendToCustomer(TransferCommand): pass
class CollectFromCustomer(TransferCommand): pass
