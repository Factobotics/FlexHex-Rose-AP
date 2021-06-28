import random
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from main import app
import config
from helpers.redis import RedisDB
# client = TestClient(app)


@pytest.fixture()
async def client():
    async with AsyncClient(
        app=app,
        base_url="{}://{}".format(config.MODULE_PROTOCOL, config.MODULE_IP)
    ) as client, LifespanManager(app):
        yield client


@pytest.fixture()
async def redis():
    yield RedisDB(host=config.REDIS_IP, port=config.REDIS_PORT, database=config.REDIS_DB)


async def clean_redis(redis):
    await redis.set_key("influxdb_buckets", "{}")
    await redis.set_key("influxdb_measurements", "{}")
    await redis.set_key("influxdb_organizations", "{}")
    await redis.set_key("influxdb_server",
                        '{"token": "'+config.INFLUXDB_TOKEN+'", \
                            "url": "'+config.INFLUXDB_PROTOCOL+'://' +
                        config.INFLUXDB_IP+':' +
                        config.INFLUXDB_PORT+'"}')


async def close_redis_connection(redis):
    await redis.close_connection()
    closed = (await redis.check_connection())
    print(await redis.check_connection())
    print(closed)
    assert closed


async def delete_key(redis, key):
    assert key in ("influxdb_buckets", "influxdb_measurements",
                   "influxdb_organizations")
    await redis.delete_key(key)


async def delete_subscription():
    async with AsyncClient() as client:
        response = await client.get("http://192.168.0.198:1026/v2/subscriptions")
        if response.text:
            subscriptions = response.json()
            for subscription in subscriptions:
                if subscription["description"].find("Test_measurement") > -1:
                    await client.delete(
                        "http://192.168.0.198:1026/v2/subscriptions/" +
                        subscription["id"]
                    )


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.text.find("Welcome to ROSE-AP application!") > -1


@pytest.mark.asyncio
async def test_measurements(client):
    response = await client.get("/measurements")
    assert response.status_code == 200
    assert response.text.find("Get measurement information") > -1
    assert response.text.find("Add measurement") > -1
    assert response.text.find("Update measurement") > -1
    assert response.text.find("Delete measurement") > -1


@pytest.mark.asyncio
async def test_buckets(client):
    response = await client.get("/buckets")
    assert response.status_code == 200
    assert response.text.find("Get bucket information") > -1
    assert response.text.find("Add bucket") > -1
    assert response.text.find("Update bucket") > -1
    assert response.text.find("Delete bucket") > -1


@pytest.mark.asyncio
async def test_subscriptions(client):
    response = await client.get("/subscriptions")
    assert response.status_code == 200
    assert response.text.find("Show measurement subscription") > -1
    assert response.text.find("Subscribe to measurement") > -1
    assert response.text.find("Pause or resume measurement subscription") > -1
    assert response.text.find("Delete measurement subscription") > -1


@pytest.mark.asyncio
async def test_organizations(client):
    response = await client.get("/organizations")
    assert response.status_code == 200
    assert response.text.find("Get organization information") > -1
    assert response.text.find("Add organization") > -1
    assert response.text.find("Update organization") > -1
    assert response.text.find("Delete organization") > -1


@pytest.mark.asyncio
async def test_get_measurements(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    response = await client.get("/get_measurements")
    assert response.status_code == 200
    assert "Test_measurement" in response.json()


@pytest.mark.asyncio
async def test_get_measurement(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    response = await client.get("/get_measurement/"+"Test_measurement")
    assert response.status_code == 200
    assert "Test_measurement" in response.json()


@pytest.mark.asyncio
async def test_get_undefined_measurement(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    undefined_measurement_name = "Undefined_measurement"
    response = await client.get("/get_measurement/"+undefined_measurement_name)
    assert response.status_code == 404
    assert response.text.find("Measurement {} not found".format(
        undefined_measurement_name)) > -1


@pytest.mark.asyncio
async def test_add_measurement(client, redis):
    response = await client.post("/add_measurement",
                                 json={
                                     "measurement": "Test_measurement",
                                     "measurement_data": {
                                         "influx_data": {
                                             "fields": {
                                                 "x": "platform_x"
                                             },
                                             "tags": {
                                                 "hexapod": "id"
                                             }
                                         },
                                         "subscription_data": {
                                             "entities": [
                                                 {
                                                     "id": ".", "id_type": "pattern",
                                                     "type": "Hexapod", "type_type": "pattern"
                                                 }
                                             ]
                                         }
                                     }
                                 })
    assert response.status_code == 201
    assert response.text.find(
        "Measurement {} added".format("Test_measurement")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_measurement(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    response = await client.post("/update_measurement/Test_measurement",
                                 json={
                                     "measurement_data": {
                                         "influx_data": {
                                             "fields": {
                                                 "x": "platform_y"
                                             },
                                             "tags": {
                                                 "hexapod": "id"
                                             }
                                         },
                                         "subscription_data": {
                                             "entities": [
                                                 {
                                                     "id": ".", "id_type": "pattern",
                                                     "type": "Hexapod", "type_type": "pattern"
                                                 }
                                             ]
                                         }
                                     }
                                 })
    assert response.status_code == 202
    assert response.text.find(
        "Measurement {} updated".format("Test_measurement")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_undefined_measurement(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    undefined_measurement_name = "Undefined_measurement"
    response = await client.post("/update_measurement/"+undefined_measurement_name,
                                 json={
                                     "measurement_data": {
                                         "measurements": [
                                             "Test_measurement",
                                             "Test_measurement_updated"
                                         ]
                                     }
                                 })
    assert response.status_code == 404
    assert response.text.find("Measurement {} not found".format(
        undefined_measurement_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_measurement(client, redis):
    await test_add_measurement(client, redis)
    response = await client.delete("/delete_measurement/"+"Test_measurement")
    assert response.status_code == 200
    assert response.text.find(
        "Measurement {} deleted".format("Test_measurement")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_undefined_measurement(client, redis):
    await test_add_measurement(client, redis)
    undefined_measurement_name = "Undefined_measurement"
    response = await client.delete("/delete_measurement/"+undefined_measurement_name)
    assert response.status_code == 404
    assert response.json()["detail"].find(
        "Measurement {} not found".format(undefined_measurement_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_get_organizations(client, redis):
    await clean_redis(redis)
    await test_add_organization(client, redis)
    response = await client.get("/get_organizations")
    assert response.status_code == 200
    assert "Test_organization" in response.json()


@pytest.mark.asyncio
async def test_get_organization(client, redis):
    await clean_redis(redis)
    await test_add_organization(client, redis)
    response = await client.get("/get_organization/"+"Test_organization")
    assert response.status_code == 200
    assert "Test_organization" in response.json()


@pytest.mark.asyncio
async def test_get_undefined_organization(client, redis):
    await clean_redis(redis)
    await test_add_organization(client, redis)
    undefined_organization_name = "Undefined_organization"
    response = await client.get("/get_organization/"+undefined_organization_name)
    assert response.status_code == 404
    assert response.text.find("Organization {} not found".format(
        undefined_organization_name)) > -1


@pytest.mark.asyncio
async def test_add_organization(client, redis):
    response = await client.post("/add_organization",
                                 json={
                                     "organization": "Test_organization",
                                     "organization_data": {
                                         "buckets": ["Test_bucket"]
                                     }
                                 })
    assert response.status_code == 201
    assert response.text.find(
        "Organization {} added".format("Test_organization")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_organization(client, redis):
    await clean_redis(redis)
    await test_add_organization(client, redis)
    response = await client.post("/update_organization/Test_organization",
                                 json={
                                     "organization_data": {
                                         "measurements": [
                                             "Test_measurement",
                                             "Test_measurement_updated"
                                         ]
                                     }
                                 })
    assert response.status_code == 202
    assert response.text.find(
        "Organization {} updated".format("Test_organization")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_undefined_organization(client, redis):
    await clean_redis(redis)
    await test_add_organization(client, redis)
    undefined_organization_name = "Undefined_organization"
    response = await client.post("/update_organization/"+undefined_organization_name,
                                 json={
                                     "organization_data": {
                                         "organizations": [
                                             "Test_organization",
                                             "Test_organization_updated"
                                         ]
                                     }
                                 })
    assert response.status_code == 404
    assert response.text.find("Organization {} not found".format(
        undefined_organization_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_organization(client, redis):
    await test_add_organization(client, redis)
    response = await client.delete("/delete_organization/"+"Test_organization")
    assert response.status_code == 200
    assert response.text.find(
        "Organization {} deleted".format("Test_organization")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_undefined_organization(client, redis):
    await test_add_organization(client, redis)
    undefined_organization_name = "Undefined_organization"
    response = await client.delete("/delete_organization/"+undefined_organization_name)
    assert response.status_code == 404
    assert response.json()["detail"].find(
        "Organization {} not found".format(undefined_organization_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_get_buckets(client, redis):
    await clean_redis(redis)
    await test_add_bucket(client, redis)
    response = await client.get("/get_buckets")
    assert response.status_code == 200
    assert "Test_bucket" in response.json()


@pytest.mark.asyncio
async def test_get_bucket(client, redis):
    await clean_redis(redis)
    await test_add_bucket(client, redis)
    response = await client.get("/get_bucket/"+"Test_bucket")
    assert response.status_code == 200
    assert "Test_bucket" in response.json()


@pytest.mark.asyncio
async def test_get_undefined_bucket(client, redis):
    await clean_redis(redis)
    await test_add_bucket(client, redis)
    undefined_bucket_name = "Undefined_bucket"
    response = await client.get("/get_bucket/"+undefined_bucket_name)
    assert response.status_code == 404
    assert response.text.find(
        "Bucket {} not found".format(undefined_bucket_name)) > -1


@pytest.mark.asyncio
async def test_add_bucket(client, redis):
    response = await client.post("/add_bucket",
                                 json={
                                     "bucket": "Test_bucket",
                                     "bucket_data": {
                                         "measurements": ["Test_measurement"]
                                     }
                                 })
    assert response.status_code == 201
    assert response.text.find("Bucket {} added".format("Test_bucket")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_bucket(client, redis):
    await clean_redis(redis)
    await test_add_bucket(client, redis)
    response = await client.post("/update_bucket/Test_bucket",
                                 json={
                                     "bucket_data": {
                                         "measurements": [
                                             "Test_measurement",
                                             "Test_measurement_updated"
                                         ]
                                     }
                                 })
    assert response.status_code == 202
    assert response.text.find("Bucket {} updated".format("Test_bucket")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_undefined_bucket(client, redis):
    await clean_redis(redis)
    await test_add_bucket(client, redis)
    undefined_bucket_name = "Undefined_bucket"
    response = await client.post("/update_bucket/"+undefined_bucket_name,
                                 json={
                                     "bucket_data": {
                                         "buckets": ["Test_bucket", "Test_bucket_updated"]
                                     }
                                 })
    assert response.status_code == 404
    assert response.text.find(
        "Bucket {} not found".format(undefined_bucket_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_bucket(client, redis):
    await test_add_bucket(client, redis)
    response = await client.delete("/delete_bucket/"+"Test_bucket")
    assert response.status_code == 200
    assert response.text.find("Bucket {} deleted".format("Test_bucket")) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_delete_undefined_bucket(client, redis):
    await test_add_bucket(client, redis)
    undefined_bucket_name = "Undefined_bucket"
    response = await client.delete("/delete_bucket/"+undefined_bucket_name)
    assert response.status_code == 404
    assert response.json()["detail"].find(
        "Bucket {} not found".format(undefined_bucket_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_no_buckets_organizations(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 406
    assert response.json()["detail"].find(
        "No organizations or buckets matched") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 200
    assert response.text.find("Successfully inserted data into InfluxDB.") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_undefined_measurement(client, redis):
    await clean_redis(redis)
    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "test_wrong"
                                         }
                                     }]
                                 })
    assert response.status_code == 404
    assert response.json()["detail"] == "Measurement not found"
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_no_fields(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 406
    assert response.json()["detail"] == "No fields matched"
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_no_organizations(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 406
    assert response.json()["detail"].find(
        "No organizations or buckets matched") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_no_buckets(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_organization(client, redis)

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 406
    assert response.json()["detail"].find(
        "No organizations or buckets matched") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_undefined_buckets_config(client, redis):
    await clean_redis(redis)
    await delete_key(redis, "influxdb_buckets")

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 500
    assert response.json()["detail"].find("Buckets config undefined") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_undefined_organizations_config(client, redis):
    await clean_redis(redis)
    await delete_key(redis, "influxdb_organizations")

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 500
    assert response.json()["detail"].find(
        "Organizations config undefined") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_undefined_measurements_config(client, redis):
    await clean_redis(redis)
    await delete_key(redis, "influxdb_measurements")

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": [{
                                         "id": "hexapod1",
                                         "platform_x": random.randint(1, 1000),
                                         "platform_y": random.randint(1, 1000),
                                         "platform_z": random.randint(1, 1000),
                                         "metadata": {
                                             "measurement": "Test_measurement"
                                         }
                                     }]
                                 })
    assert response.status_code == 500
    assert response.json()["detail"].find("Measurements config undefined") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_end_point_no_data(client, redis):
    await clean_redis(redis)

    response = await client.post("/end_point",
                                 json={
                                     "subscriptionId": "Test id",
                                     "data": []
                                 })
    assert response.status_code == 500
    assert response.json()["detail"].find("No subscription data") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_get_config(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)

    response = await client.get("/get_config/organizations")
    assert response.status_code == 200
    assert response.text.find("Test_organization") > -1

    response = await client.get("/get_config/buckets")
    assert response.status_code == 200
    assert response.text.find("Test_bucket") > -1

    response = await client.get("/get_config/measurements")
    assert response.status_code == 200
    assert response.text.find("Test_measurement") > -1

    response = await client.get("/get_config/server")
    assert response.status_code == 200
    assert response.text.find("token") > -1

    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_get_config_no_data(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)

    config_name = "Test_config"
    response = await client.get("/get_config/"+config_name)
    assert response.status_code == 422
    print(response.json())
    assert response.text.find("value is not a valid enumeration member") > -1

    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_update_config(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)

    response = await client.post("/update_config/organizations", json={"config_updated": True})
    assert response.status_code == 200
    assert response.text.find("config_updated") > -1

    response = await client.post("/update_config/buckets", json={"config_updated": True})
    assert response.status_code == 200
    assert response.text.find("config_updated") > -1

    response = await client.post("/update_config/measurements", json={"config_updated": True})
    assert response.status_code == 200
    assert response.text.find("config_updated") > -1

    response = await client.post("/update_config/server", json={"config_updated": True})
    assert response.status_code == 200
    assert response.text.find("config_updated") > -1

    await close_redis_connection(redis)


@pytest.mark.asyncio
# no other subscriptions
async def test_subscribe_to_measurement_blank(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)
    await delete_subscription()

    response = await client.post("/subscribe_to_measurement/Test_measurement")
    assert response.status_code == 200
    print(response.text)
    assert response.text.find(
        "Subscription for {} measurement was created.".format("Test_measurement")) > -1
    assert response.text.find("No other subscriptions found") > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_subscribe_to_undefined_measurement(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)
    await delete_subscription()
    undefined_measurement_name = "Undefined_measurement"
    response = await client.post("/subscribe_to_measurement/"+undefined_measurement_name)
    assert response.status_code == 404
    print(response.text)
    assert response.text.find("Measurement {} not found.".format(
        undefined_measurement_name)) > -1
    await close_redis_connection(redis)


@pytest.mark.asyncio
async def test_subscribe_to_measurement_no_entities(client, redis):
    await clean_redis(redis)
    await test_add_measurement(client, redis)
    await test_add_bucket(client, redis)
    await test_add_organization(client, redis)
    await delete_subscription()

    undefined_measurement_name = "Undefined_measurement"
    response = await client.post("/subscribe_to_measurement/"+undefined_measurement_name)
    assert response.status_code == 404
    print(response.text)
    assert response.text.find("Measurement {} not found.".format(
        undefined_measurement_name)) > -1
    await close_redis_connection(redis)
