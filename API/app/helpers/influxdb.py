from influxdb_client import InfluxDBClient, Point
# from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write_api import ASYNCHRONOUS
import logging
import traceback
from datetime import datetime
from .helpers import get_time, iso_time, get_timedelta_seconds


logger = logging.getLogger("influx")

class InfluxDB:
    def __init__(self,
        url="http://127.0.0.1:8086",
        token=None,
        org=None,
        bucket=None,
        write_options=ASYNCHRONOUS):
        self.url=url
        self.token=token
        self.org=org
        self.bucket=bucket
        self.write_options=write_options
        self.client = None
        self.write_api = None

    def get_client(self):
        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=self.write_options)

    def write_data(self, org=None, bucket=None, records=None):
        if not org: org = self.org
        if not bucket: bucket = self.bucket
        if not records: return False

        try:
            if self.write_api != None:
                self.write_api.write(bucket=bucket, org=org, record=records)
                return True
            else:
                self.get_client()
                assert self.write_api != None
                self.write_api.write(bucket=bucket, org=org, record=records)
                return True
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

    def close(self):
        self.client.close()