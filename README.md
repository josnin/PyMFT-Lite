# PyMFT-Lite 🚀

A lightweight, **cloud-agnostic**, and ubiquitous Managed File Transfer (MFT) engine. Built with **Hexagonal Architecture** (Cosmic Python) to ensure your file transfer logic remains identical whether you are on-premise or in the cloud.

---

## 🏗 System Design

PyMFT-Lite uses a **Ports and Adapters** pattern. This separates "What" the business does (Moving Files) from "How" it does it (AWS S3, SFTP, Local Disk).

### The Architecture Flow:
`Entry Point (Watcher/Lambda)` ➔ `Command (Intent)` ➔ `Message Bus` ➔ `Handler (Logic)` ➔ `Adapters (Infra)`

---

## 🛠 How to Use & Extend

### 1. Swapping Adapters (Infrastructure Agnostic)
To change a storage provider (e.g., swapping **AWS S3** for **Azure Blob**), you never touch the business logic. You only update the **Bootstrap**.

1.  **Define Adapter**: Create a new class in `src/adapters/storage.py` implementing the `Storage` port.
2.  **Plug it in**: Update `src/bootstrap/prod.py` (or `dev.py`) to use the new adapter.

```python
# In src/bootstrap/prod.py
def bootstrap():
    # Swap S3 for Azure easily:
    # cloud_adapter = storage.S3Adapter(bucket="prod-bucket")
    cloud_adapter = storage.AzureBlobAdapter(container="prod-files")
    
    return base_bootstrap(uow, cloud_adapter, onprem_adapter)
```

### 2. Adding a New Command
Commands represent a new Intent (a request to the system).
1. Create Command: Add a dataclass in src/application/commands.py.

```python
@dataclass
class ArchiveOldFiles(Command):
    days_old: int
    src_provider: str = "aws"
```

2. Register: Map the command to a handler in src/application/handlers/__init__.py.
```python
COMMAND_HANDLERS = {
    commands.ArchiveOldFiles: archive.handle_cleanup,
}
```

### 3. Adding a New Use Case (Handler)
Handlers are the Orchestrators. They contain the ubiquitous language of the business process.

1. Write Logic: Create src/application/handlers/archive.py.
2. Use Dependencies: Use the injected uow and storage_map.

```python
def handle_cleanup(cmd, uow, storage_map):
    storage = storage_map[cmd.src_provider]
    with uow:
        storage.delete_older_than(cmd.days_old)
        uow.commit()
```

## Deployment & Entry Points
PyMFT-Lite is designed to be event-driven and environment-aware.

### On-Premise (Watcher)
Monitors a local folder and triggers a ProcessInbound command when a file arrives.

```bash
export APP_ENV=prod
python -m src.entry_points.watcher
```

### Cloud Native (AWS Lambda)
Triggered by S3 bucket events. The Lambda simply parses the event into a Command and hands it to the MessageBus.
* Handler: src.entry_points.lambda_func.handler

### Local Development
No AWS or SFTP needed. Uses .env.dev and LocalStorageAdapter to mock everything on your hard drive.

```bash
export APP_ENV=dev
python -m src.entry_points.watcher
```

### 🔐 Environment Setup
Create the following files in the root directory:
* .env.dev: For local mocking (Local DB, Local Folders).
* .env.prod: For production (Postgres URL, S3 Buckets, SFTP Creds).

