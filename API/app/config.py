
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
env_path = Path('./') / '.env'
load_dotenv(dotenv_path=env_path)

levels = {'CRITICAL': logging.CRITICAL,
          'ERROR': logging.ERROR,
          'WARNING': logging.WARNING,
          'INFO': logging.INFO,
          'DEBUG': logging.DEBUG,
          'NOTSET': logging.NOTSET
          }

DEMO = False
if os.getenv('DEMO', None).lower() in ('true', '1', 't'):
    DEMO = True

LOGS_LEVEL = logging.NOTSET
if os.getenv('LOGS_LEVEL').upper() in levels:
    LOGS_LEVEL = levels[os.getenv('LOGS_LEVEL')]
LOGS_PATH = os.getenv('LOGS_PATH', './logs/')
LOGS_FILENAME = os.getenv('LOGS_FILENAME', "app.log")
LOGS_MAX_FILESIZE = int(os.getenv('LOGS_MAX_FILESIZE', str(5*1024*1024)))
LOGS_BACKUP_COUNT = int(os.getenv('LOGS_BACKUP_COUNT', '0'))

OCB_PROTOCOL = os.getenv('OCB_PROTOCOL', "http")
OCB_IP = os.getenv('OCB_IP', "127.0.0.1")
OCB_PORT = os.getenv('OCB_PORT', '1026')

MODULE_PROTOCOL = os.getenv('MODULE_PROTOCOL', "http")
MODULE_IP = os.getenv('MODULE_IP', "127.0.0.1")
MODULE_PORT = str(os.getenv('MODULE_PORT', '5000'))

REDIS_IP = os.getenv('REDIS_IP', "127.0.0.1")
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '6'))

INFLUXDB_PROTOCOL = os.getenv('INFLUXDB_PROTOCOL', "https")
INFLUXDB_IP = os.getenv('INFLUXDB_IP', "127.0.0.1")
INFLUXDB_PORT = str(os.getenv('INFLUXDB_PORT', '8086'))
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', None)


if os.getenv('PRINT_CONFIG', None).lower() in ('true', '1', 't'):
    print(os.getenv('LOGS_LEVEL'))
    print(os.getenv('LOGS_PATH'))
    print(os.getenv('LOGS_FILENAME'))
    print(int(os.getenv('LOGS_MAX_FILESIZE')))
    print(int(os.getenv('LOGS_BACKUP_COUNT')))
    print(os.getenv('OCB_PROTOCOL'))
    print(os.getenv('OCB_IP'))
    print(os.getenv('OCB_PORT'))
    print(os.getenv('MODULE_PROTOCOL'))
    print(os.getenv('MODULE_IP'))
    print(os.getenv('MODULE_PORT'))
    print(os.getenv('REDIS_IP'))
    print(int(os.getenv('REDIS_PORT')))
    print(int(os.getenv('REDIS_DB')))
    print(os.getenv('INFLUXDB_PROTOCOL'))
    print(os.getenv('INFLUXDB_IP'))
    print(str(os.getenv('INFLUXDB_PORT')))
