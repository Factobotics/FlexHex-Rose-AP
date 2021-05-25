from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import orjson
import logging

logger = logging.getLogger("buckets")

router = APIRouter(tags=['buckets'])
templates = Jinja2Templates(directory="templates")


@router.get("/buckets", response_class=HTMLResponse)
async def buckets(request: Request):
    """
    ## Buckets page.
    """
    return templates.TemplateResponse("buckets.html", {"request": request})


@router.get("/get_buckets")
async def get_buckets(request: Request):
    """
    ## Get a list of available buckets.

    Takes bucket object from redis and returns keys of it.
    """
    redis = request.app.state.redis
    buckets = orjson.loads(await redis.get_key("influxdb_buckets"))
    return [bucket for bucket in buckets]


@router.get("/get_bucket/{bucket}")
async def get_bucket(request: Request, bucket: str):
    """
    ## Get data of the selected bucket.
    
    Returns object with key as bucket name and value as bucket data.

    - **bucket**: bucket name.
    """
    redis = request.app.state.redis
    buckets = orjson.loads(await redis.get_key("influxdb_buckets"))
    if bucket not in buckets:
        logger.warning("Bucket {} not found.".format(bucket))
        raise HTTPException(
            status_code=404, detail="Bucket {} not found.".format(bucket))
    return {bucket: buckets[bucket]}


@router.post("/add_bucket")
async def add_bucket(request: Request, data: dict):
    """
    ## Create a new bucket.

    Bucket also has to exists inside Influx-db.
    
    - **data**:
        - **bucket**: new bucket name.
        - **bucket_data**: new bucket data.
    """
    redis = request.app.state.redis
    buckets = orjson.loads(await redis.get_key("influxdb_buckets"))
    buckets[data["bucket"]] = data["bucket_data"]

    await redis.set_key("influxdb_buckets", orjson.dumps(buckets))
    logger.info("Bucket {} added.".format(data['bucket']))
    return HTMLResponse(content="Bucket {} added.".format(data['bucket']), status_code=200)


@router.post("/update_bucket/{bucket}")
async def update_bucket(request: Request, bucket: str, data: dict):
    """
    ## Update selected bucket.

    Overwrites selected bucket with new data.

    - **bucket**: bucket name.
    - **data**:
        - **bucket_data**: bucket data to overwrite the existing one.
    """

    redis = request.app.state.redis
    buckets = orjson.loads(await redis.get_key("influxdb_buckets"))
    if bucket not in buckets:
        logger.warning("Bucket {} not found.".format(bucket))
        raise HTTPException(
            status_code=404, detail="Bucket {} not found.".format(bucket))
    buckets[bucket] = data["bucket_data"]
    await redis.set_key("influxdb_buckets", orjson.dumps(buckets))
    logger.info("Bucket {} updated.".format(bucket))
    return HTMLResponse(content="Bucket {} updated.".format(bucket), status_code=200)


@router.delete("/delete_bucket/{bucket}")
async def delete_bucket(request: Request, bucket: str):
    """
    ## Delete selected bucket.

    - **bucket**: bucket name.
    """

    redis = request.app.state.redis
    buckets = orjson.loads(await redis.get_key("influxdb_buckets"))
    if bucket not in buckets:
        logger.warning("Bucket {} not found.".format(bucket))
        raise HTTPException(
            status_code=404, detail="Bucket {} not found.".format(bucket))
    buckets.pop(bucket, None)
    await redis.set_key("influxdb_buckets", orjson.dumps(buckets))
    logger.info("Bucket {} deleted.".format(bucket))
    return HTMLResponse(content="Bucket {} deleted.".format(bucket), status_code=200)
