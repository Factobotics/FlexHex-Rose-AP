# Getting started

### :warning: Short notice :warning:

**Influx-db variables** variables in the **.env** file must be changed to your influx-db service variables. Other variables can be ignored to try out the module.

### Configuring system dependent settings.

Files can be edited with text editor of your choice (Notepad, Notepad++, VSCode, Nano, Atom).

- **docker-compose.yaml** - Container orchestration configuration.
    - file location:  
    ```rose-ap/docker-compose.yaml```  
    - services:
        - **api**: Project application.
        - **orion**: Orion Context Broker.
        - **mongo**: MongoDB database for Orion Context Broker.
        - **redis**: Redis database for application data storage.
    
- **Dockerfiles** - Files defining Docker containers
    - file locations:  
    ```rose-ap/API/Dockerfile```
    
- **.env** - Configuration file for project application.

    There is no need to edit this file to try the module. This **file can be hidden** so you might need to adjust your system settings.

    - **File location**:  
    ```rose-ap/API/app/.env```  
    - **Variables**:
        - **General variables**:
            - PRINT_CONFIG - If set to *true*, prints the whole configuration when application workers start.
        - **Logging variables**:
            - LOGS_LEVEL - Logging level. Default - NOTSET. Available - NOTSET, DEBUG, INFO, WARNING, CRITICAL.
            - LOGS_PATH - Path of the log file. **docker-compose.yaml** must be updated accordingly, so the log files would be exposed outside of the container.
            - LOGS_FILENAME - Name of the log file.
            - LOGS_MAX_FILESIZE - Maximum allowed size for the log file in **bytes**. After file exceeds this number, new file is created and old one is renamed or deleted based on backup count below.
            - LOGS_BACKUP_COUNT - How many old log files to keep. (based on LOGS_MAX_FILESIZE variable)
        - **Orion Context Broker**:
            - OCB_PROTOCOL - *http* or secure *https* connection. (http || https)
            - OCB_IP - IP adress of the Orion Context Broker.
            - OCB_PORT - Port number of the Orion Context Broker.
        - **Module variables**:
            - MODULE_PROTOCOL - *http* or secure *https* connection. (http || https)
            - MODULE_IP - IP adress of the module.
            - MODULE_PORT - Port number of the module.
        - **Redis variables**:
            - REDIS_IP - IP adress of the Redis service.
            - REDIS_PORT - Port number of the Redis service.
            - REDIS_DB - Database to use inside Redis.
        - **Influx-db variables**:
            - INFLUXDB_PROTOCOL - *http* or secure *https* connection. (http || https)
            - INFLUXDB_IP - IP adress of the Influx-db service.
            - INFLUXDB_PORT - Port number of the Influx-db service.
            - INFLUXDB_TOKEN - Token from Influx-db, to allow uploading data on defined organizations and buckets.


### Running docker-compose.

- Open terminal 
    - Linux users: **```CTRL + SHIFT + T```**
    - Windows users: **```Windows key + X```** and then press **A** key (For administrator access).
- Navigate to **rose-ap** folder.
- Launch the docker compose:  
    ```docker-compose up --build```  
- It can take some time for all of the images to be pulled from the internet and then builded, so please be patient.
- Expected behavior:
    - A lot of logs should be appearing in the terminal.
    - While browsing the terminal it should be seen that *api 1, mongo 1, orion 1* and *redis 1* containers are running and none of them exited due to error. 
    - If one or more containers writes ```<container_name> exited <0 or 1>``` something bad happened during initialization. 
    - In case of failure:
        - You can try to redo the steps.
        - Browse the logs in the terminal to figure out why and what crashed.
        - Browse logs in the ```rose-ap/API/app/logs```, for the module logs to look for errors.
        - Go to [Trouble shooting](trouble-shooting.md) documentation page for known bugs.
- When docker-compose finishes you can close the terminal, but general logs won't be visible anymore. To view the logs from containers, do the **Launch the docker compose** step again in the **rose-ap** directory.
- Find your computer or docker host IP address. 
    - Linux users (in terminal):   
        ```hostname -I``` or ```ifconfig```  
    - Windows users (in terminal / command prompt):  
        ```ipconfig /all```  
- Open your (computer or docker host) address via web-browser.
    - :warning: Add the **5000** port number to the address.
    - Example:
        - ```http://192.168.0.50:5000```
- After some loading for the first time the UI and the *Welcome page* should be displayed.

### Orion Context Broker.

Orion Context Broker API user guide can be found [here](https://fiware-orion.readthedocs.io/en/1.8.0/user/walkthrough_apiv2/index.html).

- **To check Orion Context Broker version** (and test if it is alive):
    - Go to:
        - ```<your IP address>:1026/version```
    - Example:
        - ```http://192.168.0.50:1026/version```
<br>

- **To check and create required OCB entities**:
    - Go to:
        - ```<your IP address>:1026/v2/entities```
    - Example:
        - ```http://192.168.0.50:1026/v2/entities```
    <br>

    After going through the OCB user guide, you will be somewhat familiar with the Orion Context Broker and comfortable enough to create some entities. 
    
    This can be done using one of the REST clients or tools that you installed in the [Installations steps](installationguide.md) or using curl requests in the terminal. 
    
    Create as many entities as you want, assign **id** and **type** and other desired data. 
    
    :warning: Most importantly, the module requires entities to have ***metadata*** object with ***measurement*** key.
    
    This is used to identify measurement of the entity when the subscription sends data to the module's end point.
    
    To the entity variable, just add ```"metadata": {"measurement": <measurement name>}``` while creating it.

    - Example entity in almost any of the REST client/tool:

        ```<POST REQUEST> to 192.168.0.50:1026/v2/entities?options=keyValues```
        ``` 
        {
            "id": "hexapod1",
            "type": "Hexapod",
            "platform_x": 0,
            "platform_y": 0,
            "platform_z": 0,
            "metadata": {
                "measurement": "hexapod_position"
            }
        }
        ```
    - Example using curl:
        ```
        curl 192.168.0.50:1026/v2/entities?options=keyValues -s -S -H 'Content-Type: application/json' -d @- <<EOF
        {
            "id": "hexapod1",
            "type": "Hexapod",
            "platform_x": 0,
            "platform_y": 0,
            "platform_z": 0,
            "metadata": {
                "measurement": "hexapod_position"
            }
        }
        EOF
        ```
<br>

- **To check OCB subscriptions**:
    - Go to:
        - ```<your IP address>:1026/v2/subscriptions```
    - Example:
        - ```http://192.168.0.50:1026/v2/subscriptions```
    <br>

    By default, no subscriptions should be available.
    
    Creating and managing Orion Context Broker subscriptions for measurements will be explained in the steps below.


### Using WEB interface.

By default, you will be greeted with the welcome landing page, shortly describing further steps and other pages.

You can navigate pages using the NavBar on the left of the page. 

- **Measurements:**

    To start using the system, measurements should be defined. 

    Measurement defines how module treats and processes subscription data from Orion Context Broker. 

    When subscription data is received, the module automatically translates variables to fields and tags for the Influx-db in Line Protocol.  

    You can define *measurements* in **Measurements** page.

    By default, there should be one measurement available. It should be compatible with your created entity, if you used the provided example above. You can check this measurement data in **Measurements** page, **Get measurement information** tab.

