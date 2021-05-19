import logging
import traceback
from datetime import datetime, timezone
import time
from enum import Enum 

def get_time():
    # local_time = datetime.utcnow()
    # return local_time
    return datetime.now(timezone.utc).timestamp()

def iso_time(time):
    return datetime.utcnow().isoformat("T") + "Z"

def get_timedelta_seconds(time_1, time_2):
    return (datetime.fromtimestamp(time_2) - datetime.fromtimestamp(time_1)).seconds


class ConfigName(str, Enum):
    server = "server"
    organizations = "organizations"
    buckets = "buckets"
    measurements = "measurements"