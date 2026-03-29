import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.bootstrap.dev import bootstrap as dev_bootstrap
from src.bootstrap.prod import bootstrap as prod_bootstrap
from src.application.commands import ProcessInbound

class InboundWatcher(FileSystemEventHandler):
    def __init__(self, bus):
        self.bus = bus

    def on_created(self, event):
        if event.is_directory: return
        self.bus.handle(ProcessInbound(
            src_path=event.src_path,
            dest_path=f"uploads/{os.path.basename(event.src_path)}"
        ))

if __name__ == "__main__":
    env = os.getenv("APP_ENV", "dev")
    bus = prod_bootstrap() if env == "prod" else dev_bootstrap()
    
    observer = Observer()
    observer.schedule(InboundWatcher(bus), "./inbox")
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
