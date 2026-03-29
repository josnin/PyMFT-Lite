import logging

logger = logging.getLogger(__name__)

def notify_slack_on_transfer(event, slack_client):
    """Event Handler: Send notification after file is moved."""
    message = f"✅ File {event.file_hash[:8]} transferred to {event.dest_path}"
    slack_client.send(message)
    logger.info("Slack notification sent.")

def update_audit_dashboard(event, api_client):
    """Event Handler: Sync status with external monitoring tool."""
    api_client.post_status(event.file_hash, status="ARCHIVED")
