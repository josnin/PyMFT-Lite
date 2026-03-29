import os
from dotenv import load_dotenv
from src.adapters import storage, repository, slack
from src.application import unit_of_work
from .base import base_bootstrap

def bootstrap():
    load_dotenv(".env.prod") # Or skip if using Lambda Envs
    uow = unit_of_work.SqlAlchemyUnitOfWork(repository.PostgresRepo(os.getenv("DB_URL")))
    
    storage_map = {
        "aws": storage.S3Adapter(bucket=os.getenv("S3_BUCKET")),
        "onprem": storage.SFTPAdapter(host=os.getenv("ONPREM_HOST"), user="svc_mft"),
        "customer": storage.SFTPAdapter(host=os.getenv("CUST_HOST"), user="cust_user")
    }
    
    slack_client = slack.SlackAdapter(token=os.getenv("SLACK_TOKEN"))
    
    return base_bootstrap(uow, storage_map, slack_adapter=slack_client)
