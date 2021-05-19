from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import orjson
import logging

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
    organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
    return [org for org in organizations]


@router.get("/get_organization/{org}")
async def get_organization(request: Request, org: str):
    """
    ## Get orgnization object of the selected organization.
    
    Returns organization object with key as organization name and value as organization data.

    - **org**: measurement name.
    """

    redis = request.app.state.redis
    organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations:
        logger.warning("Organization {} not found.".format(org))
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    return {org: organizations[org]}


@router.post("/add_organization")
async def add_organization(request: Request, data: dict):
    """
    ## Create a new organization.

    - **data**:
        - **organization**: new organization name.
        - **organization_data**: new organization data.
    """
    redis = request.app.state.redis
    organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
    organizations[data["organization"]] = data["organization_data"]
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations))
    logger.info("Organization {} added".format(data['organization']))
    return HTMLResponse(content="Organization {} added".format(data['organization']), status_code=200)


@router.post("/update_organization/{org}")
async def update_organization(request: Request, org: str, data: dict):
    """
    ## Update selected organization.

    Overwrites selected organization with new data.

    - **org**: organization name.
    - **data**:
        - **organization_data**: orgnization data to be overwrite existing one.
    """
    redis = request.app.state.redis
    organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations:
        logger.warning("Organization {} not found.".format(org))
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    organizations[org] = data["organization_data"]
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations))
    logger.info("Organization {} updated".format(org))
    return HTMLResponse(content="Organization {} updated".format(org), status_code=200)


@router.delete("/delete_organization/{org}")
async def delete_organization(request: Request, org: str):
    """
    ## Delete selected organization.

    - **org**: organization name.
    """

    redis = request.app.state.redis
    organizations = orjson.loads(await redis.get_key("influxdb_organizations"))
    if org not in organizations:
        logger.warning("Organization {} not found.".format(org))
        raise HTTPException(
            status_code=404, detail="Organization {} not found.".format(org))
    organizations.pop(org, None)
    await redis.set_key("influxdb_organizations", orjson.dumps(organizations))
    logger.info("Orgnization {} deleted".format(org))
    return HTMLResponse(content="Orgnization {} deleted".format(org), status_code=200)
