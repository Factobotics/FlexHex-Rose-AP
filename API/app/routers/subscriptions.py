import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import orjson
import httpx

logger = logging.getLogger("subscriptions")

router = APIRouter(tags=['subscriptions'])
templates = Jinja2Templates(directory="templates")


@router.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions(request: Request):
    """
    ## Subscriptions page.
    """
    return templates.TemplateResponse("subscriptions.html", {"request": request})


@router.post("/subscribe_to_measurement/{measurement}")
async def subscribe_to_measurement(request: Request, measurement: str):
    """
    ## Subscribe to selected measurement.

    If no subscriptions found, new one will be created.
    (Also when no subscriptions are available at all)

    If subscription already exists for this measurement,
    it will be updated.

    If more than one subscription exists for this measurement,
    all of them will be deleted and new one will be created.

    - **measurement**: measurement name to subscribe to.
    """
    redis = request.app.state.redis
    config = request.app.state.config

    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement and measurement not in measurements:
        logger.warning("%s measurement was not found.", measurement)
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))
    # global subscription_template

    #   subscription_obj = subscription_template.copy()
    subscription_obj = {
        "description": "ROSE-AP generated subscription.",
        "subject": {
            "entities": [],
            "condition": {}},
        "notification": {
            "http": {
                "url": "{}://{}:{}/end_point".format(
                    config.MODULE_PROTOCOL,
                    config.MODULE_IP,
                    config.MODULE_PORT)},
            "attrs": [],
            "attrsFormat": "keyValues"
        }
    }

    measurement_obj = measurements[measurement]

    entities = []
    condition_attrs = []
    notification_attrs = []

    for entity in measurement_obj["subscription_data"]["entities"]:
        temp_obj = {}
        if entity["id_type"] == "pattern":
            temp_obj["idPattern"] = entity["id"]
        elif entity["id_type"] == "exact":
            temp_obj["id"] = entity["id"]
        else:
            logger.warning(
                "Wrong entity ID pattern string. ID type: %s. Measurement: %s",
                entity["id_type"],
                measurement
            )
            raise HTTPException(
                status_code=422,
                detail="Wrong entity ID pattern string. ID type: {}. Measurement: {}".format(
                    entity["id_type"],
                    measurement
                )
            )

        if entity["type_type"] == "pattern":
            temp_obj["typePattern"] = entity["type"]
        elif entity["type_type"] == "exact":
            temp_obj["type"] = entity["type"]
        else:
            logger.warning("Wrong entity TYPE pattern string. Type type: %s. Measurement: %s",
                           entity["type_type"], measurement)
            raise HTTPException(
                status_code=422,
                detail="Wrong entity TYPE pattern string. Type type: {}. Measurement: {}".format(
                    entity["type_type"],
                    measurement
                )
            )
        entities.append(temp_obj)

        if len(entities) == 0:
            logger.warning(
                "No entities found for %s measurement.", measurement)
            raise HTTPException(
                status_code=404,
                detail="No entities found for {} measurement.".format(
                    measurement
                )
            )

    temp_object = {**measurement_obj["influx_data"]
                   ["tags"], **measurement_obj["influx_data"]["fields"]}
    for field in temp_object:
        if temp_object[field] != "id" and temp_object[field] != "metadata":
            condition_attrs.append(temp_object[field])

        notification_attrs.append(temp_object[field])

    if len(notification_attrs) == 0:
        logger.warning(
            "No notification attributes found for %s measurement.", measurement)
        raise HTTPException(
            status_code=404,
            detail="No notification attributes found for {} measurement.".format(
                measurement
            )
        )

    if "metadata" not in notification_attrs:
        notification_attrs.append("metadata")

    subscription_obj["subject"]["entities"] = entities
    subscription_obj["subject"]["condition"]["attrs"] = condition_attrs
    subscription_obj["notification"]["attrs"] = notification_attrs
    subscription_obj["description"] = subscription_obj["description"] + \
        " Measurement: " + measurement

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "{}://{}:{}/v2/subscriptions?options=keyValues".format(
                config.ocb_http_protocol,
                config.OCB_IP,
                config.OCB_PORT
            )
        )
        if resp.status_code != 200:
            logger.error("Failed to get subscriptions.")
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())
        response_data = resp.json()
        subscriptions_obj = []
        if response_data:
            for sub in response_data:
                if (sub["description"].find(measurement) > -1 and
                        sub["description"].find("ROSE-AP") > -1):
                    subscriptions_obj.append(sub)
            if len(subscriptions_obj) > 1:
                # ----------------------------------------------------
                # More than one subscription
                logger.warning(
                    "More than one subscription found. \
                    Purging these subscriptions and creating a new one.")
                for sub in subscriptions_obj:
                    resp = await client.delete(
                        '{}://{}:{}/v2/subscriptions/{}?options=keyValues'.format(
                            config.ocb_http_protocol,
                            config.OCB_IP,
                            config.OCB_PORT,
                            sub["id"]
                        )
                    )
                    if resp.status_code != 204:
                        logger.error(
                            "Failed to delete %s subscription \
                            for %s measurement.",
                            sub,
                            measurement
                        )
                        logger.error(resp.json())
                        raise HTTPException(
                            status_code=resp.status_code, detail=resp.json())
                resp = await client.post(
                    '{}://{}:{}/v2/subscriptions?options=keyValues'.format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT
                    ),
                    json=subscription_obj
                )
                if resp.status_code == 201:
                    logger.info(
                        "Created subscription for %s measurement. Duplicates were purged.",
                        measurement
                    )
                    return HTMLResponse(
                        content="Created subscription for {} measurement. \
                            Duplicates were purged.".format(
                            measurement
                        ),
                        status_code=200
                    )

                logger.error(
                    "Failed to create subscription for %s measurement. \
                        Duplicates were purged.", measurement)
                logger.error(resp.json())
                raise HTTPException(
                    status_code=resp.status_code, detail=resp.json())
                # ----------------------------------------------------
            if len(subscriptions_obj) == 1:
                # ----------------------------------------------------
                # One subscription found
                logger.info("Subscription matched.")
                resp = await client.patch(
                    '{}://{}:{}/v2/subscriptions/{}?options=keyValues'.format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT,
                        subscription_obj[0]["id"]
                    ),
                    json=subscription_obj
                )
                if resp.status_code == 204:
                    logger.info(
                        "Updated subscription for %s measurement.", measurement)
                    return HTMLResponse(
                        content="Updated subscription for {} measurement.".format(
                            measurement
                        ),
                        status_code=200
                    )
                logger.error(
                    "Failed to update subscription for %s measurement.", measurement)
                logger.error(resp.json())
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=resp.json()
                )
                # ----------------------------------------------------
            if len(subscriptions_obj) == 0:
                # ----------------------------------------------------
                # No subscriptions found
                logger.info(
                    "No subscription matched. \
                        Trying to create subscription for %s measurement.",
                    measurement
                )
                resp = await client.post(
                    '{}://{}:{}/v2/subscriptions?options=keyValues'.format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT
                    ),
                    json=subscription_obj
                )
                if resp.status_code == 201:
                    logger.info(
                        "Created subscription for %s measurement.", measurement)
                    return HTMLResponse(
                        content="Created subscription for {} measurement.".format(
                            measurement
                        ),
                        status_code=200
                    )
                logger.error(
                    "Failed to create subscription for %s measurement.", measurement)
                logger.error(resp.json())
                raise HTTPException(
                    status_code=resp.status_code, detail=resp.json())
                # ----------------------------------------------------
        else:
            logger.info("Subscriptions list was empty.")
            resp = await client.post(
                '{}://{}:{}/v2/subscriptions?options=keyValues'.format(
                    config.ocb_http_protocol,
                    config.OCB_IP,
                    config.OCB_PORT
                ),
                json=subscription_obj
            )
            if resp.status_code == 201:
                logger.info(
                    "Subscription for %s measurement was created. \
                        No other subscriptions found.",
                    measurement
                )
                return HTMLResponse(
                    content="Subscription for {} measurement was created. \
                        No other subscriptions found.".format(
                        measurement
                    ),
                    status_code=200
                )
            logger.error(
                "Failed to create subscription for %s measurement. \
                    No other subscriptions found.",
                measurement
            )
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())


@router.get("/get_measurement_subscription/{measurement}")
async def get_measurement_subscription(request: Request, measurement: str):
    """
    ## Get data of the selected measurement subscription.

    Returns response from Orion Context Broker about subscription.

    - **measurement**: measurement name.
    """

    redis = request.app.state.redis
    config = request.app.state.config

    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("%s measurement was not found.", measurement)
        raise HTTPException(
            status_code=404, detail="{} measurement was not found.".format(measurement))

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "{}://{}:{}/v2/subscriptions?options=keyValues".format(
                config.ocb_http_protocol,
                config.OCB_IP,
                config.OCB_PORT)
        )
        if resp.status_code != 200:
            logger.error("Failed to get subscriptions.")
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())
        response_data = resp.json()
        subscription_obj = []
        if response_data:
            for sub in response_data:
                if (sub["description"].find(measurement) > -1 and
                        sub["description"].find("ROSE-AP") > -1):
                    subscription_obj.append(sub)
            if len(subscription_obj) == 0:
                logger.info(
                    "No subscriptions found for %s measurement.", measurement)
                raise HTTPException(
                    status_code=404,
                    detail="No subscriptions found for {} measurement.".format(
                        measurement)
                )
            return subscription_obj
        logger.info("No subscriptions found.")
        raise HTTPException(
            status_code=404, detail="No subscriptions found.")


@router.patch("/pause_measurement_subscription/{measurement}")
async def pause_measurement_subscription(request: Request, measurement: str):
    """
    ## Pause subscription of the selected measurement.

    Sets subscription status to "inactive".

    - **measurement**: measurement name.
    """
    redis = request.app.state.redis
    config = request.app.state.config

    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("%s measurement was not found.", measurement)
        raise HTTPException(
            status_code=404, detail="{} measurement was not found.".format(measurement))

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "{}://{}:{}/v2/subscriptions?options=keyValues".format(
                config.ocb_http_protocol,
                config.OCB_IP,
                config.OCB_PORT)
        )
        if resp.status_code != 200:
            logger.error("Failed to get subscriptions.")
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())
        response_data = resp.json()
        subscriptions_obj = []
        if response_data:
            for sub in response_data:
                if (sub["description"].find(measurement) > -1 and
                        sub["description"].find("ROSE-AP") > -1):
                    subscriptions_obj.append(sub)
            if len(subscriptions_obj) == 0:
                logger.info(
                    "No subscriptions found for %s measurement.", measurement)
                raise HTTPException(
                    status_code=404,
                    detail="No subscriptions found for {} measurement.".format(
                        measurement)
                )
            for sub in subscriptions_obj:
                resp = await client.patch(
                    "{}://{}:{}/v2/subscriptions/{}?options=keyValues".format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT,
                        sub["id"]
                    ),
                    json={"status": "inactive"}
                )
                if resp.status_code == 204:
                    logger.info(
                        "%s measurement subscription paused.", measurement)
                    return HTMLResponse(
                        content="{} measurement subscription paused.".format(
                            measurement
                        ),
                        status_code=200
                    )
                logger.error(
                    "Something failed pausing %s measurement subscription.", measurement)
                logger.error(resp.json())
                raise HTTPException(
                    status_code=resp.status_code, detail=resp.text)
        else:
            logger.info("No subscriptions found.")
            raise HTTPException(
                status_code=404, detail="No subscriptions found.")


@router.patch("/resume_measurement_subscription/{measurement}")
async def resume_measurement_subscription(request: Request, measurement: str):
    """
    ## Resumes paused subscription of the selected measurement.

    Sets subscription status to "active".

    - **measurement**: measurement name.
    """
    redis = request.app.state.redis
    config = request.app.state.config

    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("%s measurement was not found.", measurement)
        raise HTTPException(
            status_code=404, detail="{} measurement was not found.".format(measurement))

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "{}://{}:{}/v2/subscriptions?options=keyValues".format(
                config.ocb_http_protocol,
                config.OCB_IP,
                config.OCB_PORT)
        )
        if resp.status_code != 200:
            logger.error("Failed to get subscriptions.")
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())
        response_data = resp.json()
        subscriptions_obj = []
        if response_data:
            for sub in response_data:
                if (sub["description"].find(measurement) > -1 and
                        sub["description"].find("ROSE-AP") > -1):
                    subscriptions_obj.append(sub)
            if len(subscriptions_obj) == 0:
                logger.info(
                    "No subscriptions found for %s measurement.", measurement)
                raise HTTPException(
                    status_code=404,
                    detail="No subscriptions found for {} measurement.".format(
                        measurement)
                )
            for sub in subscriptions_obj:
                resp = await client.patch(
                    "{}://{}:{}/v2/subscriptions/{}?options=keyValues".format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT,
                        sub["id"]
                    ),
                    json={"status": "active"}
                )
                if resp.status_code == 204:
                    logger.info(
                        "%s measurement subscription resumed.", measurement)
                    return HTMLResponse(
                        content="{} measurement subscription resumed.".format(
                            measurement
                        ),
                        status_code=200
                    )
                logger.error(
                    "Something failed resuming %s measurement subscription.", measurement)
                logger.error(resp.json())
                raise HTTPException(
                    status_code=resp.status_code, detail=resp.text)
        else:
            logger.info("No subscriptions found.")
            raise HTTPException(
                status_code=404, detail="No subscriptions found.")


@router.delete("/delete_measurement_subscription/{measurement}")
async def delete_measurement_subscription(request: Request, measurement: str):
    """
    ## Deletes subscription of the selected measurement.

    - **measurement**: measurement name.
    """
    redis = request.app.state.redis
    config = request.app.state.config

    measurements = orjson.loads(await redis.get_key("influxdb_measurements"))
    if measurement not in measurements:
        logger.warning("%s measurement was not found.", measurement)
        raise HTTPException(
            status_code=404, detail="Measurement {} not found.".format(measurement))

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "{}://{}:{}/v2/subscriptions?options=keyValues".format(
                config.ocb_http_protocol,
                config.OCB_IP,
                config.OCB_PORT)
        )
        if resp.status_code != 200:
            logger.error("Failed to get subscriptions.")
            logger.error(resp.json())
            raise HTTPException(
                status_code=resp.status_code, detail=resp.json())
        response_data = resp.json()
        subscriptions_obj = []
        if response_data:
            for sub in response_data:
                if (sub["description"].find(measurement) > -1 and
                        sub["description"].find("ROSE-AP") > -1):
                    subscriptions_obj.append(sub)
            if len(subscriptions_obj) == 0:
                logger.info(
                    "No subscriptions found for %s measurement.", measurement)
                raise HTTPException(
                    status_code=404,
                    detail="No subscriptions found for {} measurement.".format(
                        measurement)
                )
            for sub in subscriptions_obj:
                resp = await client.delete(
                    "{}://{}:{}/v2/subscriptions/{}?options=keyValues".format(
                        config.ocb_http_protocol,
                        config.OCB_IP,
                        config.OCB_PORT,
                        sub["id"]))
                if resp.status_code != 204:
                    logger.error(
                        "Something failed deleting %s measurement subscription.", measurement)
                    logger.error(resp.json())
                    raise HTTPException(
                        status_code=resp.status_code, detail=resp.text)
            logger.info(
                "%s measurement subscriptions deleted.", measurement)
            return HTMLResponse(
                content="Subscription deleted for {} measurement.".format(
                    measurement), status_code=200)
        logger.info("No subscriptions found.")
        raise HTTPException(
            status_code=404, detail="No subscriptions found.")
