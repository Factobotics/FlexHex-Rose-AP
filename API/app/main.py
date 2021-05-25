from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging, traceback, sys, orjson
from logging.handlers import RotatingFileHandler
import httpx

import config
from helpers.CustomFormatter import CustomFormatter

rotating_file_handler = RotatingFileHandler(
  filename=config.logs_path+config.logs_filename,
  mode='a',
  maxBytes=config.logs_max_filesize,
  backupCount=config.logs_backup_count
)

stdout_logger = logging.StreamHandler(
  sys.stdout
)
stdout_logger.setFormatter(CustomFormatter())

logging.basicConfig(
  level=config.log_level,
  format='%(levelname)s: %(asctime)s - [%(name)s:%(funcName)s](%(filename)s:%(lineno)d) - %(message)s',
  datefmt="%y-%m-%d %H:%M:%S",
  handlers=[rotating_file_handler, stdout_logger]
)


logger = logging.getLogger("rose-ap")

from routers import buckets, organizations, measurements, subscriptions
from helpers.influxdb import InfluxDB
from helpers.helpers import iso_time, get_time, ConfigName
from helpers.redis import RedisDB

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(buckets.router)
app.include_router(organizations.router)
app.include_router(measurements.router)
app.include_router(subscriptions.router)

influxdb_server = {
  "token": config.influxdb_token,
  "url": "{}://{}:{}".format(config.influxdb_protocol, config.influxdb_ip, config.influxdb_port)
}

influxdb_organizations = { "Test": { "buckets": [ "Test"] } }

influxdb_buckets = { "Test": { "measurements": [ "hexapod_position"] } }

influxdb_measurements = { "hexapod_position": { "subscription_data": { "entities": [ { "id": ".", "id_type": "pattern", "type": "Hexapod", "type_type": "pattern" } ], "throttling": 0 }, "influx_data": { "tags": { "hexapod": "id" }, "fields": { "x": "platform_x", "y": "platform_y", "z": "platform_z" } } } }

subscription_template = { "description": "ROSE-AP generated subscription.", "subject": { "entities": [], "condition": {} }, "notification": { "http": { "url": config.module_protocol + "://"+config.module_ip+":"+config.module_port+"/end_point" }, "attrs": [], "attrsFormat": "keyValues" } }


@app.on_event("startup")
async def startup_event():
  logger.info("Rose-AP starting...")
  redis = RedisDB(host=config.redis_ip, port=config.redis_port, db=config.redis_db)
  influxdb = InfluxDB(url=influxdb_server.get("url"), token=influxdb_server.get("token"))

  app.state.redis = redis
  app.state.influxdb = influxdb
  app.state.config = config

  if not await redis.get_key("influxdb_server"):
    await redis.set_key("influxdb_server", orjson.dumps(influxdb_server))
  if not await redis.get_key("influxdb_organizations"):
    await redis.set_key("influxdb_organizations", orjson.dumps(influxdb_organizations))
  if not await redis.get_key("influxdb_buckets"):
    await redis.set_key("influxdb_buckets", orjson.dumps(influxdb_buckets))
  if not await redis.get_key("influxdb_measurements"):
    await redis.set_key("influxdb_measurements", orjson.dumps(influxdb_measurements))
  logger.info("ROSE-AP init finished. App started.")

  if config.demo == True:
    async with httpx.AsyncClient() as client:
      body = {"id": "hexapod1", "type": "Hexapod", "platform_x": 0, "platform_y": 0,
              "platform_z": 0, "metadata": {"measurement": "hexapod_position"}}
      resp = await client.post("{}://{}:{}/v2/entities?options=keyValues".format(config.ocb_http_protocol, config.ocb_ip, config.ocb_port), 
      json=body)
      if resp.status_code != 200 or resp.status_code != 200 and resp.json()["description"] == "Already Exists":
        logger.debug("Demo entity created!")
      else:
        logger.warning("Failed to create demo entity!")


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def root(request: Request):
  """
  ## Welcome / Landing page of the module
  """
  return templates.TemplateResponse("welcome.html", {"request": request})


@app.post("/end_point", tags=["main"])
async def end_point(subscription_data: dict):
  """
  ## Endpoint to receive data from Orion Context Broker

  Module validates data.

  Checks if measurement in metadata is found.

  Checks if it has valid Organizations and Buckets assigned to the measurement.

  Uploads formatted line protocol data into Influx database.

  - **subscription_data**: formed subscription data from OCB.
  """
  logger.debug(["Raw data: ", subscription_data])

  data = subscription_data.get("data")
  if not data:
    logger.error("No subscription data.")
    raise HTTPException(status_code=500, detail="No subscription data.")

  redis = app.state.redis

  if not redis.get_key("influxdb_buckets"):
    logger.error("Buckets config undefined.")
    raise HTTPException(
      status_code=500, detail="Buckets config undefined.")
  elif not redis.get_key("influxdb_measurements"):
    logger.error("Measurements config undefined.")
    raise HTTPException(
      status_code=500, detail="Measurements config undefined.")
  elif not redis.get_key("influxdb_organizations"):
    logger.error("Organizations config undefined.")
    raise HTTPException(
      status_code=500, detail="Organizations config undefined.")

  # records = []
  records = {}
  found_org = False
  
  measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
  organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
  buckets = orjson.loads(await redis.get_key("influxdb_buckets"))


  for entity in data:
    measurement_data = measurements.get(entity["metadata"]["measurement"])
    if measurement_data is None:
      raise HTTPException(
        status_code=404, detail="Measurement not found")
    measurement = entity["metadata"]["measurement"]
    logger.debug(["Measurement: ", measurement])
    logger.debug(["Entity measurement: ", entity["metadata"]["measurement"]])
    tags = {}
    fields = {}
    for tag in measurement_data["influx_data"]["tags"]:
      logger.debug(["tag: ", tag])
      for var1 in entity:
        logger.debug(["entity var:", var1])
        if measurement_data["influx_data"]["tags"][tag] == var1:
          tags[tag] = entity[var1]
    for field in measurement_data["influx_data"]["fields"]:
      logger.debug(["field: ", field])
      for var2 in entity:
        logger.debug(["entity var:", var2])
        if measurement_data["influx_data"]["fields"][field] == var2:
          fields[field] = entity[var2]

    if not tags:
      logger.warning("No tags found")
    if not fields:
      logger.error(["No fields matched", subscription_data])
      raise HTTPException(status_code=406, detail="No fields matched")

    insert_object = {
      "measurement": measurement,
      "tags": tags,
      "fields": fields
    }
    logger.info(["Insert object: ", insert_object])

    
    for org in organizations:
      for bucket in organizations.get(org, {}).get("buckets", []):
        for measurement_temp in buckets.get(bucket, {}).get("measurements", {}):
          if measurement == measurement_temp:
            found_org = True
            logger.debug(["Organization: ", org])
            logger.debug(["Bucket: ", bucket])
            logger.debug(["Measurement temp: ", measurement_temp])
            logger.debug(["Measurement: ", measurement])
            insert_object["time"] = iso_time(get_time())
            # records.append(insert_object)
            if not records.get(org): 
              records[org] = {}
            if not records.get(org).get(bucket):
              records[org][bucket] = []
            records[org][bucket].append(insert_object)
    
    logger.debug(["Records:", records])

    if not found_org:
      logger.error("No organizations or buckets matched for {} measurement.".format(measurement))
      raise HTTPException(status_code=406, detail="No organizations or buckets matched for {} measurement.".format(measurement))
  
  logger.info("Trying to push data to InfluxDB...")
  influxdb = app.state.influxdb

  for org in records:
    for bucket in records[org]:
      influxdb.write_data(org=org, bucket=bucket, records=records[org][bucket])

  logger.info("Successfully inserted data into InfluxDB.")
  return HTMLResponse(content="Successfully inserted data into InfluxDB.", status_code=200)


@app.get("/get_config/{config}", tags=["config"])
async def get_config(config: ConfigName):
  """
  ## Returns full config that is stored in redis.

  - **config**: config name to be returned.
  """
  if config == "server":
    return orjson.loads(await app.redis.get_key("influxdb_server"))
  elif config == "organizations":
    return orjson.loads(await app.redis.get_key("influxdb_organizations"))
  elif config == "buckets":
    return orjson.loads(await app.redis.get_key("influxdb_buckets"))
  elif config == "measurements":
    return orjson.loads(await app.redis.get_key("influxdb_measurements"))
  else:
    raise HTTPException(status_code=404, detail="Config {} not found.".format(config))


@app.post("/update_config/{config}", tags=["config"])
async def update_config(config: ConfigName, value: dict):
  """
  ## Overrides whole config that is stored in redis.

  - **config**: config name to be updated.
  """
  if config == "server":
    await app.redis.set_key("influxdb_server", orjson.dumps(value))
    return orjson.loads(await app.redis.get_key("influxdb_server"))
  elif config == "organizations":
    await app.redis.set_key("influxdb_organizations", orjson.dumps(value))
    return orjson.loads(await app.redis.get_key("influxdb_organizations"))
  elif config == "buckets":
    await app.redis.set_key("influxdb_buckets", orjson.dumps(value))
    return orjson.loads(await app.redis.get_key("influxdb_buckets"))
  elif config == "measurements":
    await app.redis.set_key("influxdb_measurements", orjson.dumps(value))
    return orjson.loads(await app.redis.get_key("influxdb_measurements"))
  else:
    raise HTTPException(status_code=404, detail="Config {} not found.".format(config))

  
@app.on_event("shutdown")
async def shutdown_event():
  app.state.influxdb.close()
  app.state.redis.close_connection()
  logger.info("Rose-AP showdown")
