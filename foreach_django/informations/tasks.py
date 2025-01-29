from celery import shared_task
from .services import send_message_to_subscriber_sync

@shared_task
def send_scheduled_message(chat_id, message, img_path=None, video_path=None):
    success = send_message_to_subscriber_sync(chat_id, message, img_path, video_path)
    return success
