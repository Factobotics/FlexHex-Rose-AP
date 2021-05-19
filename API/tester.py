import requests
import asyncio
import random
import functools
import httpx
import time
# async def spam():
#     loop = asyncio.get_event_loop()
#     futures1 = [loop.run_in_executor(
#         None, functools.partial(
#         requests.post, 
#         'http://127.0.0.1:1026/v2/entities/hexapod1/attrs?options=keyValues', 
#         json={"platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)}
#     )) for _ in range(1000)]
#     futures2=[loop.run_in_executor(
#         None, functools.partial(
#         requests.post, 
#         'http://127.0.0.1:1026/v2/entities/hexapod2/attrs?options=keyValues', 
#         json={"platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)}
#     )) for _ in range(1000)]
#     futures3=[loop.run_in_executor(
#         None, functools.partial(
#         requests.post, 
#         'http://127.0.0.1:1026/v2/entities/hexapod3/attrs?options=keyValues', 
#         json={"platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)}
#     )) for _ in range(1000)]
#     futures4=[loop.run_in_executor(
#         None, functools.partial(
#         requests.post, 
#         'http://127.0.0.1:1026/v2/entities/hexapod4/attrs?options=keyValues', 
#         json={"platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)}
#     )) for _ in range(1000)]

#     # for future in futures1+futures2+futures3+futures4:
#     #     await future
#     await asyncio.gather(futures1)
#     # for future in futures2:
#     #     await future
#     # for future in futures3:
#     #     await future
#     # for future in futures4:
#     #     await future
#     # requests.get(
#     #     'http://127.0.0.1:1026/v2/entities/hexapod1/attrs?options=keyValues',
#     #     {
#     #     "platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)
#     #     })

# loop = asyncio.get_event_loop()
# loop.run_until_complete(spam())



async def get_async(hexapod, requests_amount):
    async with httpx.AsyncClient() as client:
        started = time.time()
        await asyncio.gather(*[client.post('http://127.0.0.1:1026/v2/entities/'+hexapod+'/attrs?options=keyValues', 
        json={"platform_" + random.choice(['x', 'y', 'z']): random.randint(-50000, 50000)}) for _ in range(requests_amount)])
        print(requests_amount, " requests took: ", time.time() - started, "s")
async def launch(requests_amount):
    started_whole = time.time()
    await asyncio.gather(*[get_async('hexapod1', requests_amount), get_async('hexapod2', requests_amount), get_async('hexapod3', requests_amount), get_async('hexapod4', requests_amount)])
    print(requests_amount*4, " requests took (whole concurrent): ", time.time()-started_whole, 's')
asyncio.run(launch(10000))