jwt_access_token = ''
from datetime import datetime, timedelta
import requests

URL='http://127.0.0.1:8000/taskService/createTask'
headers = {
    "Authorization": f"Bearer {jwt_access_token}"
}

frequency_choices=[
        ('NONE', 'No Repeat'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
priority_choices=[
        ('LOW', 'Low'),
        ('MED', 'Medium'),
        ('HIGH', 'High'),
    ]
class TaskModel:

    def __init__(self, name, description, frequency, due_date, priority):
        self.name = name
        self.description = description
        self.frequency = frequency
        self.due_date = due_date
        self.priority = priority


due_date = datetime.now()
task_index = 1
for freq_label in frequency_choices:
    for priority_label in priority_choices:
        name = f'Task {task_index}'
        description = f'Description {task_index}'
        task = TaskModel(name, description, freq_label[0], str(due_date), priority_label[0])
        task_payload = task.__dict__
        print(task_payload)
        response = requests.post(url=URL, json=task_payload, headers=headers)
        print(response.status_code)
        task_index += 1
        due_date += timedelta(days=1)

