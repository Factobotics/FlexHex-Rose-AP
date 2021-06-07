"""
Main FastAPI app and endpoint for subscription data.
"""


from logging.handlers import RotatingFileHandler
import logging
import sys
import orjson
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from helpers.redis import RedisDB
from helpers.helpers import iso_time, ConfigName
from helpers.influxdb import InfluxDB
from helpers.CustomFormatter import CustomFormatter
import config
from routers import buckets, organizations, measurements, subscriptions

rotating_file_handler = RotatingFileHandler(
    filename=config.LOGS_PATH+config.LOGS_FILENAME,
    mode='a',
    maxBytes=config.LOGS_MAX_FILESIZE,
    backupCount=config.LOGS_BACKUP_COUNT
)

stdout_logger = logging.StreamHandler(
    sys.stdout
)
stdout_logger.setFormatter(CustomFormatter())

logging.basicConfig(
    level=config.LOGS_LEVEL,
    format='%(levelname)s: %(asctime)s - \
    [%(name)s:%(funcName)s](%(filename)s:%(lineno)d) - %(message)s',
    datefmt="%y-%m-%d %H:%M:%S",
    handlers=[rotating_file_handler, stdout_logger]
)


logger = logging.getLogger("rose-ap")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(buckets.router)
app.include_router(organizations.router)
app.include_router(measurements.router)
app.include_router(subscriptions.router)

influxdb_server = {
    "token": config.INFLUXDB_TOKEN,
    "url": "{}://{}:{}".format(config.INFLUXDB_PROTOCOL, config.INFLUXDB_IP, config.INFLUXDB_PORT)
}

influxdb_organizations = {"Test": {"buckets": ["Test"]}}

influxdb_buckets = {"Test": {"measurements": ["hexapod_position"]}}

influxdb_measurements = {
    "hexapod_position":
    {
        "subscription_data":
        {
            "entities": [
                {
                    "id": ".",
                    "id_type": "pattern",
                    "type": "Hexapod",
                    "type_type": "pattern"
                }
            ], "throttling": 0
        },
        "influx_data": {
            "tags": {"hexapod": "id"},
            "fields": {
                "x": "platform_x",
                "y": "platform_y",
                "z": "platform_z"}
        }}}

# subscription_template = {
#     "description": "ROSE-AP generated subscription.",
#     "subject": {
#         "entities": [],
#         "condition": {}},
#     "notification": {
#         "http": {
#             "url": "{}://{}:{}/end_point".format(
#                 config.MODULE_PROTOCOL,
#                 config.MODULE_IP,
#                 config.MODULE_PORT
#             )
#         },
#         "attrs": [],
#         "attrsFormat": "keyValues"
#     }
# }


@app.on_event("startup")
async def startup_event():
    logger.info("Rose-AP starting...")
    redis = RedisDB(host=config.REDIS_IP,
                    port=config.REDIS_PORT, database=config.REDIS_DB)
    influxdb = InfluxDB(url=influxdb_server.get(
        "url"), token=influxdb_server.get("token"))

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

    if config.DEMO:
        async with httpx.AsyncClient() as client:
            body = {"id": "hexapod1", "type": "Hexapod", "platform_x": 0, "platform_y": 0,
                    "platform_z": 0, "metadata": {"measurement": "hexapod_position"}}
            resp = await client.post(
                "{}://{}:{}/v2/entities?options=keyValues".format(
                    config.OCB_PROTOCOL,
                    config.OCB_IP,
                    config.OCB_PORT
                ), json=body)
            if resp.status_code == 200:
                logger.debug("Demo entity created!")
            elif resp.json()["description"] == "Already Exists":
                logger.debug("Demo entity already existed.")
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
    if not redis.get_key("influxdb_measurements"):
        logger.error("Measurements config undefined.")
        raise HTTPException(
            status_code=500, detail="Measurements config undefined.")
    if not redis.get_key("influxdb_organizations"):
        logger.error("Organizations config undefined.")
        raise HTTPException(
            status_code=500, detail="Organizations config undefined.")

    # records = []
    records = {}
    found_org = False

    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    buckets_obj = orjson.loads(await redis.get_key("influxdb_buckets"))

    for entity in data:
        measurement_data = measurements_obj.get(
            entity["metadata"]["measurement"])
        if measurement_data is None:
            raise HTTPException(
                status_code=404, detail="Measurement not found")
        measurement = entity["metadata"]["measurement"]
        logger.debug(["Measurement: ", measurement])
        logger.debug(
            ["Entity measurement: ", entity["metadata"]["measurement"]])
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

        for org in organizations_obj:
            for bucket in organizations_obj.get(org, {}).get("buckets", []):
                for measurement_temp in buckets_obj.get(bucket, {}).get("measurements", {}):
                    if measurement == measurement_temp:
                        found_org = True
                        logger.debug(["Organization: ", org])
                        logger.debug(["Bucket: ", bucket])
                        logger.debug(["Measurement temp: ", measurement_temp])
                        logger.debug(["Measurement: ", measurement])
                        insert_object["time"] = iso_time()
                        # records.append(insert_object)
                        if not records.get(org):
                            records[org] = {}
                        if not records.get(org).get(bucket):
                            records[org][bucket] = []
                        records[org][bucket].append(insert_object)

        logger.debug(["Records:", records])

        if not found_org:
            logger.error(
                'No organizations or buckets matched for %measurement measurement.')
            raise HTTPException(
                status_code=406,
                detail="No organizations or buckets matched for {} measurement.".format(
                    measurement)
            )

    logger.info("Trying to push data to InfluxDB...")
    influxdb = app.state.influxdb

    for org in records:
        for bucket in records[org]:
            influxdb.write_data(org=org, bucket=bucket,
                                records=records[org][bucket])

    logger.info("Successfully inserted data into InfluxDB.")
    return HTMLResponse(content="Successfully inserted data into InfluxDB.", status_code=200)


@app.get("/get_config/{desired_config}", tags=["config"])
async def get_config(desired_config: ConfigName):
    """
    ## Returns full config that is stored in redis.

    - **desired_config**: config name to be returned.
    """
    redis = app.redis
    if desired_config == "server":
        return orjson.loads(await redis.get_key("influxdb_server"))
    if desired_config == "organizations":
        return orjson.loads(await redis.get_key("influxdb_organizations"))
    if desired_config == "buckets":
        return orjson.loads(await redis.get_key("influxdb_buckets"))
    if desired_config == "measurements":
        return orjson.loads(await redis.get_key("influxdb_measurements"))
    raise HTTPException(
        status_code=404, detail="Config {} not found.".format(desired_config))


@app.post("/update_config/{desired_config}", tags=["config"])
async def update_config(desired_config: ConfigName, value: dict):
    """
    ## Overrides whole config that is stored in redis.

    - **desired_config**: config name to be updated.
    """
    redis = app.redis
    if desired_config == "server":
        await redis.set_key("influxdb_server", orjson.dumps(value))
        return orjson.loads(await redis.get_key("influxdb_server"))
    elif desired_config == "organizations":
        await redis.set_key("influxdb_organizations", orjson.dumps(value))
        return orjson.loads(await redis.get_key("influxdb_organizations"))
    elif desired_config == "buckets":
        await redis.set_key("influxdb_buckets", orjson.dumps(value))
        return orjson.loads(await redis.get_key("influxdb_buckets"))
    elif desired_config == "measurements":
        await redis.set_key("influxdb_measurements", orjson.dumps(value))
        return orjson.loads(await redis.get_key("influxdb_measurements"))
    else:
        raise HTTPException(
            status_code=404, detail="Config {} not found.".format(desired_config))


@app.on_event("shutdown")
async def shutdown_event():
    app.state.influxdb.close()
    app.state.redis.close_connection()
    logger.info("Rose-AP showdown")
