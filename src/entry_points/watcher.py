import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 1. Dynamic Bootstrap Selection
env = os.getenv("APP_ENV", "dev")
if env == "prod":
    from src.bootstrap.prod import bootstrap
elif env == "uat":
    from src.bootstrap.uat import bootstrap
else:
    from src.bootstrap.dev import bootstrap

# Initialize the Message Bus with injected dependencies
bus = bootstrap()
logger = logging.getLogger(__name__)

class MFTInboundHandler(FileSystemEventHandler):
    """
    Listens for new files and converts them into 
    Application Layer Commands.
    """
    def __init__(self, message_bus):
        self.bus = message_bus

    def on_created(self, event):
        # Ignore directory creation
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        
        # Ignore temporary or hidden files (e.g., .tmp, .DS_Store)
        if filename.startswith('.') or filename.endswith('.tmp'):
            return

        logger.info(f"📂 New file detected: {event.src_path}")
        
        try:
            # Import command here to avoid circular imports
            from src.application.commands import ProcessInbound
            
            cmd = ProcessInbound(
                src_path=event.src_path,
                dest_path=f"inbound/{filename}"
            )
            
            # The bus handles retries and deduplication automatically
            self.bus.handle(cmd)
            
        except Exception as e:
            logger.error(f"❌ Failed to dispatch command for {filename}: {e}")

def run_watcher(watch_path):
    """
    Entry point function to start the persistent monitoring service.
    """
    if not os.path.exists(watch_path):
        os.makedirs(watch_path)
        logger.info(f"Created watch directory: {watch_path}")

    event_handler = MFTInboundHandler(bus)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    
    logger.info(f"🔭 PyMFT-Lite [{env}] monitoring: {watch_path}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Watcher service...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # In production, this path usually comes from an Env Var
    PATH_TO_WATCH = os.getenv("WATCH_PATH", "./inbox")
    
    logging.basicConfig(level=logging.INFO)
    run_watcher(PATH_TO_WATCH)
