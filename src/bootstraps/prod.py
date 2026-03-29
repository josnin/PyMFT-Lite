import os
from .base import base_bootstrap
from src.adapters import storage, repository, external_api
from src.application import unit_of_work

def bootstrap():
    # Production Adapters
    cloud = storage.S3Adapter(bucket=os.getenv("S3_BUCKET"))
    onprem = storage.SFTPAdapter(host=os.getenv("SFTP_HOST"), user=os.getenv("SFTP_USER"))
    
    # Audit Repo (Postgres)
    uow = unit_of_work.SqlAlchemyUnitOfWork(
        repository.PostgresRepo(os.getenv("DB_URL"))
    )

    # Optional Event Adapters
    slack = external_api.SlackClient(token=os.getenv("SLACK_TOKEN"))

    return base_bootstrap(
        uow=uow, 
        cloud_adapter=cloud, 
        onprem_adapter=onprem,
        slack_adapter=slack
    )
