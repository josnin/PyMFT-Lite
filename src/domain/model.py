from dataclasses import dataclass, field
from . import events

@dataclass
class FileTransfer:
    file_hash: str
    src_path: str
    dest_path: str
    events: list = field(default_factory=list)

    def complete(self):
        self.events.append(events.FileTransferred(
            file_hash=self.file_hash, 
            dest_path=self.dest_path
        ))

