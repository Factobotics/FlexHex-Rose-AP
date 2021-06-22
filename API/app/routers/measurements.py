import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import orjson


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
    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    return [measurement for measurement in measurements_obj]


@router.get("/get_measurement/{measurement}")
async def get_measurement(request: Request, measurement: str):
    """
    ## Get data of the selected measurement.

    Returns object with key as measurement name and value as measurement data.

    - **measurement**: measurement name.
    """
    redis = request.app.state.redis
    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements_obj:
        logger.warning("Measurement %s not found.", measurement)
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    return {measurement: measurements_obj[measurement]}


@router.post("/add_measurement", status_code=status.HTTP_201_CREATED)
async def add_measurement(request: Request, data: dict):
    """
    ## Create a new measurement.

    Measurement has to exists inside Influx-db.

    - **data**:
        - **measurement**: new measurement name.
        - **measurement_data**: new measurement data.
    """
    redis = request.app.state.redis
    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    measurement = data["measurement"]
    measurements_obj[measurement] = data["measurement_data"]
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements_obj))
    logger.info("Measurement %s added.", measurement)
    return {"message": "Measurement {} added.".format(measurement)}


@router.post("/update_measurement/{measurement}", status_code=status.HTTP_202_ACCEPTED)
async def update_measurement(request: Request, measurement: str, data: dict):
    """
    ## Update selected measurement.

    Overwrites selected measurement with new data.

    - **measurement**: measurement name.
    - **data**:
        - **measurement_data**: measurement data to overwrite the existing one.
    """

    redis = request.app.state.redis
    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements_obj:
        logger.warning("Measurement %s not found.", measurement)
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    measurements_obj[measurement] = data["measurement_data"]
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements_obj))
    logger.info("Measurement %s updated", measurement)
    return {"message": "Measurement {} updated".format(measurement)}


@router.delete("/delete_measurement/{measurement}")
async def delete_measurement(request: Request, measurement: str):
    """
    ## Delete selected measurement.

    - **measurement**: measurement name.
    """

    redis = request.app.state.redis
    measurements_obj = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements_obj:
        logger.warning("Measurement %s not found.", measurement)
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    measurements_obj.pop(measurement, None)
    await redis.set_key("influxdb_measurements", orjson.dumps(measurements_obj))
    logger.info("Measurement %s deleted", measurement)
    return HTMLResponse(content="Measurement {} deleted".format(measurement), status_code=200)
