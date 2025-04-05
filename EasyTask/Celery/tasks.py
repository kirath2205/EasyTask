import redis
from celery import Celery
from celery.signals import worker_ready


app = Celery('redis_listener', broker='redis://localhost:6379/0')
print('test redis')


# This function will handle the expiry event
def handle_expiry_event(message):
    expired_data = message['data'].decode('utf-8')
    print(f"Key expired: {expired_data}")


# Define a Celery task to listen for key expiration events
@app.task
def listen_for_expirations():
    r = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')

    print("Listening for key expiration events...")

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            handle_expiry_event(message)
