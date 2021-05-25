from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import orjson
import logging

logger = logging.getLogger("measurements")

router = APIRouter(tags=['measurements'])
templates = Jinja2Templates(directory="templates")


@router.get("/measurements", response_class=HTMLResponse)
async def measurements(request: Request):
    """
    ## Measurements page.
    """
    return templates.TemplateResponse("measurements.html", {"request": request})


@router.get("/get_measurements")
async def get_measurements(request: Request):
    """
    ## Get a list of available measurements.

    Takes measurement object from redis and returns keys of it.
    """
    redis = request.app.state.redis
    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    return [measurement for measurement in measurements]


@router.get("/get_measurement/{measurement}")
async def get_measurement(request: Request, measurement: str):
    """
    ## Get data of the selected measurement.
    
    Returns object with key as measurement name and value as measurement data.

    - **measurement**: measurement name.
    """
    redis = request.app.state.redis
    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("Measurement {} not found.".format(measurement))
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    return {measurement: measurements[measurement]}


@router.post("/add_measurement")
async def add_measurement(request: Request, data: dict):
    """
    ## Create a new measurement.

    Measurement has to exists inside Influx-db.

    - **data**:
        - **measurement**: new measurement name.
        - **measurement_data**: new measurement data.
    """
    redis = request.app.state.redis
    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    measurement = data["measurement"]
    measurements[measurement] = data["measurement_data"]
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements))
    logger.info("Measurement {} added.".format(measurement))
    return HTMLResponse(content="Measurement {} added.".format(measurement), status_code=200)


@router.post("/update_measurement/{measurement}")
async def update_measurement(request: Request, measurement: str, data: dict):
    """
    ## Update selected measurement.

    Overwrites selected measurement with new data.

    - **measurement**: measurement name.
    - **data**:
        - **measurement_data**: measurement data to overwrite the existing one.
    """

    redis = request.app.state.redis
    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("Measurement {} not found.".format(measurement))
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    measurements[measurement] = data["measurement_data"]
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements))
    logger.info("Measurement {} updated".format(measurement))
    return HTMLResponse(content="Measurement {} updated".format(measurement), status_code=200)


@router.delete("/delete_measurement/{measurement}")
async def delete_measurement(request: Request, measurement: str):
    """
    ## Delete selected measurement.

    - **measurement**: measurement name.
    """

    redis = request.app.state.redis
    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("Measurement {} not found.".format(measurement))
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    measurements.pop(measurement, None)
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements))
    logger.info("Measurement {} deleted".format(measurement))
    return HTMLResponse(content="Measurement {} deleted".format(measurement), status_code=200)
