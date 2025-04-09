from celery import shared_task


@shared_task
def handle_expiry_event(message):
    print(f"Processing a new task {message}")
    expired_data = message['data'].decode('utf-8')
    print(f"Key expired: {expired_data}")
