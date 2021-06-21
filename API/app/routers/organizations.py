import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
import orjson


logger = logging.getLogger("organizations")

router = APIRouter(tags=['organizations'])
templates = Jinja2Templates(directory="templates")


@router.get("/organizations", response_class=HTMLResponse)
async def organizations(request: Request):
    """
    ## Organizations page.
    """
    return templates.TemplateResponse("organizations.html", {"request": request})


@router.get("/get_organizations")
async def get_organizations(request: Request):
    """
    ## Get a list of all available organizations.

    Takes organizations object from redis and returns keys of it.
    """
    redis = request.app.state.redis
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    return [org for org in organizations_obj]


@router.get("/get_organization/{org}")
async def get_organization(request: Request, org: str):
    """
    ## Get data of the selected organization.

    Returns object with key as organization name and value as organization data.

    - **org**: organization name.
    """

    redis = request.app.state.redis
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations_obj:
        logger.warning("Organization %s not found.", org)
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    return {org: organizations_obj[org]}


@router.post("/add_organization")
async def add_organization(request: Request, data: dict):
    """
    ## Create a new organization.

    Organization has to exists inside Influx-db.

    - **data**:
        - **organization**: new organization name.
        - **organization_data**: new organization data.
    """
    redis = request.app.state.redis
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    organizations_obj[data["organization"]] = data["organization_data"]
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations_obj))
    logger.info("Organization %s added", data['organization'])
    return HTMLResponse(
        content="Organization {} added".format(
            data['organization']
        ),
        status_code=200
    )


@router.post("/update_organization/{org}")
async def update_organization(request: Request, org: str, data: dict):
    """
    ## Update selected organization.

    Overwrites selected organization with new data.

    - **org**: organization name.
    - **data**:
        - **organization_data**: Organization data to overwrite the existing one.
    """
    redis = request.app.state.redis
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations_obj:
        logger.warning("Organization %s not found.", org)
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    organizations_obj[org] = data["organization_data"]
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations_obj))
    logger.info("Organization %s updated", org)
    return HTMLResponse(content="Organization {} updated".format(org), status_code=200)


@router.delete("/delete_organization/{org}")
async def delete_organization(request: Request, org: str):
    """
    ## Delete selected organization.

    - **org**: organization name.
    """

    redis = request.app.state.redis
    organizations_obj = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations_obj:
        logger.warning("Organization %s not found.", org)
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    organizations_obj.pop(org, None)
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations_obj))
    logger.info("Organization %s deleted", org)
    return HTMLResponse(content="Organization {} deleted".format(org), status_code=200)
