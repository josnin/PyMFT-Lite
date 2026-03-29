import os
from dotenv import load_dotenv
from src.adapters import storage, repository
from src.application import unit_of_work
from .base import base_bootstrap

def bootstrap():
    load_dotenv(".env.dev")
    uow = unit_of_work.SqlAlchemyUnitOfWork(repository.SQLiteRepo(os.getenv("DB_URL")))
    
    # Use LocalStorageAdapter for cloud/onprem mocks
    storage_map = {
        "aws": storage.LocalStorageAdapter("./mock_cloud"),
        "onprem": storage.LocalStorageAdapter("./mock_onprem"),
        "customer": storage.LocalStorageAdapter("./mock_customer")
    }
    
    return base_bootstrap(uow, storage_map)
