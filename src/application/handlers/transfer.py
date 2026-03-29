import os
import logging
from src.domain.model import FileTransfer

logger = logging.getLogger(__name__)

def handle_transfer(cmd, uow, storage_map):
    """
    Unified Use Case: Handles all directions (Inbound, Outbound, Customer Sync).
    The 'storage_map' provides the specific adapters based on cmd providers.
    """
    # Identify Source and Destination from the Map
    source = storage_map.get(cmd.src_provider)
    destination = storage_map.get(cmd.dest_provider)

    if not source or not destination:
        raise ValueError(f"Invalid providers: {cmd.src_provider} -> {cmd.dest_provider}")

    # 1. Identity (Deduplication)
    file_hash = source.get_hash(cmd.src_path)
    
    with uow:
        # 2. Domain Rule: No Duplicates
        if uow.audit_log.exists(file_hash):
            logger.info(f"⏭️ Skipping: {cmd.src_path} (Content already moved)")
            return

        # 3. Execution (The 'Move' Fact)
        temp_path = f"/tmp/mft_{file_hash}"
        try:
            logger.info(f"🔄 Transferring {cmd.src_path} ({cmd.src_provider}) to {cmd.dest_provider}...")
            source.download(cmd.src_path, temp_path)
            destination.upload(temp_path, cmd.dest_path)
            
            # 4. Domain Logic & Fact Recording
            transfer = FileTransfer(file_hash, cmd.src_path, cmd.dest_path)
            transfer.complete() # Records 'FileTransferred' Event
            
            uow.audit_log.add(transfer)
            uow.commit() # Database save + Event Bus trigger
            logger.info(f"✅ Transfer Successful: {cmd.file_name}")
            
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
