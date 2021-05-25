
import os, logging
from pathlib import Path
from dotenv import load_dotenv
env_path = Path('./') / '.env'
load_dotenv(dotenv_path=env_path)

levels = {'CRITICAL' : logging.CRITICAL,
    'ERROR' : logging.ERROR,
    'WARNING' : logging.WARNING,
    'INFO' : logging.INFO,
    'DEBUG' : logging.DEBUG,
    'NOTSET' : logging.NOTSET
}

demo = False
if os.getenv('DEMO', False).lower() in ('true', '1', 't'):
  demo = True

logs_level = logging.NOTSET
if os.getenv('LOGS_LEVEL').upper() in levels:
  log_level = levels[os.getenv('LOGS_LEVEL')]
logs_path = os.getenv('LOGS_PATH', './logs/')
logs_filename = os.getenv('LOGS_FILENAME', "app.log")
logs_max_filesize = int(os.getenv('LOGS_MAX_FILESIZE', 5*1024*1024))
logs_backup_count = int(os.getenv('LOGS_BACKUP_COUNT', 0))

ocb_http_protocol = os.getenv('OCB_PROTOCOL', "http")
ocb_ip = os.getenv('OCB_IP', "127.0.0.1")
ocb_port = os.getenv('OCB_PORT', 1026)

module_protocol = os.getenv('MODULE_PROTOCOL', "http")
module_ip = os.getenv('MODULE_IP', "127.0.0.1")
module_port = str(os.getenv('MODULE_PORT', 5000))

redis_ip = os.getenv('REDIS_IP', "127.0.0.1")
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 6))

influxdb_protocol = os.getenv('INFLUXDB_PROTOCOL', "https")
influxdb_ip = os.getenv('INFLUXDB_IP', "127.0.0.1")
influxdb_port = str(os.getenv('INFLUXDB_PORT', 8086))
influxdb_token = os.getenv('INFLUXDB_TOKEN', None)


if os.getenv('PRINT_CONFIG', False).lower() in ('true', '1', 't'):
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