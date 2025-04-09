import redis
from EasyTask.celery import app


def listen_for_expirations():
    r = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')

    print("Listening for key expiration events...")

    for message in pubsub.listen():
        print(f"processing message {message}")
        if message['type'] == 'pmessage':
            app.send_task('TaskProcessor.tasks.handle_expiry_event', args=[message])


if __name__ == '__main__':
    listen_for_expirations()
