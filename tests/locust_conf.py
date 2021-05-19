import time
from locust import HttpUser, task, between

import random

class QuickstartUser(HttpUser):
    # wait_time = between(1, 2.5)

    @task
    def get_(self):
        self.client.post("/end_point", json={"data":[{
    "id": "hexapod1",
    "platform_x": random.randint(1, 10000),
    "platform_y": random.randint(1, 10000),
    "platform_z": random.randint(1, 10000),
    "metadata": {
        "measurement": "hexapod_position"
    }
    }]})

    # def on_start(self):
        # self.client.post("/login", json={"username":"foo", "password":"bar"})
