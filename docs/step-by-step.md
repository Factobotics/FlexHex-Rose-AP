# Step-by-step guide

### Configuring system dependent settings.

Files can be edited with text editor of your choice (Notepad, Notepad++, VSCode, Nano, Atom).

- **docker-compose.yaml** - Container orchestration configuration.
    - file location:  
    ```FlexHex-Rose-AP/docker-compose.yaml```  
    - services:
        - **api**: Project application.
        - **orion**: Orion Context Broker.
        - **mongo**: MongoDB database for Orion Context Broker.
        - **redis**: Redis database for application data storage.
        - **influxdb**: InfluxDB instance.
    <br>

- **.env** - Configuration file for ```FlexHex-Rose-AP/docker-compose.yaml```.

    This **file can be hidden** so you might need to adjust your system settings.

    - **File location**:  
    ```FlexHex-Rose-AP/.env```  
    - **Variables**:
        - DOCKER_INFLUXDB_INIT_MODE - Launch mode of the container. Can be setup or upgrade. Setup prepares the Influx-db for demo, upgrade - upgrades Influx-db from 1.x to 2.x.
        - DOCKER_INFLUXDB_INIT_USERNAME - Default users username.
        - DOCKER_INFLUXDB_INIT_PASSWORD - Default users password.
        - DOCKER_INFLUXDB_INIT_ORG - Default organization.
        - DOCKER_INFLUXDB_INIT_BUCKET - Default bucket of default organization.
        - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN - Access token for the default user. Can access and edit everything.
    <br>

- **Dockerfiles** - Files defining Docker containers
    - file locations:  
    ```FlexHex-Rose-AP/API/Dockerfile```
    <br>

- **.env** - Configuration file for project application.

    There is no need to edit this file to try the module. This **file can be hidden** so you might need to adjust your system settings.

    - **File location**:  
    ```FlexHex-Rose-AP/API/app/.env```  
    - **Variables**:
        - **General variables**:
            - PRINT_CONFIG - If set to *true*, prints the whole configuration when application workers start.
            - DEMO - Load data for demonstration.
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
    - Windows users: **```Windows key + X```** and then press **A** key.
- Navigate to **FlexHex-Rose-AP** folder.

    - ```cd FlexHex-Rose-AP```

- Launch the docker compose:  

    - ```docker-compose up --build```  

- It can take some time for all of the images to be pulled from the internet and then built, so please be patient. It can take up to 5 minutes on 100MB/s internet.

- Expected behavior:

    - A lot of logs should be appearing in the terminal.

    - While browsing the terminal it should be seen that *api 1, mongo 1, orion 1* and *redis 1* containers are running and none of them exited due to error. 

    - If one or more containers writes ```<container_name> exited <0 or 1>``` something bad happened during initialization. 

    - In case of failure:

        - You can try to redo the steps.

        - Browse the logs in the terminal to figure out why and what crashed.

        - Browse logs in the ```FlexHex-Rose-AP/API/app/logs```, for the module logs to look for errors.

        - Go to [Trouble shooting](trouble-shooting.md) documentation page for known bugs.

- When docker-compose finishes you can close the terminal, but general logs won't be visible anymore. To view the logs from containers, do the **Launch the docker compose** step again in the **FlexHex-Rose-AP** directory.

- Find your computer or docker host IP address. 

    - Linux users (in terminal):   

        - ```hostname -I``` or ```ifconfig```  

    - Windows users (in terminal / command prompt): 

        - ```ipconfig /all```  

- Open your (computer or docker host) address via web-browser.

    - ```http://<your IP>:5000```

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

- **To check and create required Orion Context Broker entities**:

    - Go to:

        - ```<your IP address>:1026/v2/entities```

    - Example:

        - ```http://192.168.0.50:1026/v2/entities```

    <br>

    After going through the Orion Context Broker user guide, you will be somewhat familiar with the Orion Context Broker and comfortable enough to create some entities. 
    
    This can be done using one of the [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) clients or tools that you installed in the [Installations steps](installationguide.md) or using curl requests in the terminal. More information about curl [here](https://en.wikipedia.org/wiki/CURL).
    
    Create as many entities as you want, assign **id** and **type** and other desired data. 
    
    :warning: Most importantly, the module requires entities to have ***metadata*** object with ***measurement*** key and value as desired measurement name.
    
    This is used to identify measurement of the entity when the subscription sends data to the module's end point.
    
    To the entity variable, just add ```"metadata": {"measurement": <measurement name>}``` while creating it.

    :warning: Example below can fail (Entity Exists), if *.env* files **DEMO** variable was set to **True** as it will create this entity automatically.

    - Example entity that can be created in almost any of the REST client/tool:

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

- **To check Orion Context Broker subscriptions**:

    - Go to:

        - ```<your IP address>:1026/v2/subscriptions```

    - Example:

        - ```http://192.168.0.50:1026/v2/subscriptions```

    <br>

    By default, no subscriptions should be available.
    
    Creating and managing Orion Context Broker subscriptions for measurements will be explained in the steps below.


### Using WEB interface.

By default, you will be greeted with the welcome landing page, shortly describing further steps and other pages.

You can navigate pages using the navigation bar on the left of the page. 

- **Measurements:**

    To start using the module, measurements are one of the things that must be defined. 

    Measurement defines how module treats and processes subscription data from Orion Context Broker. 

    When subscription data is received, the module automatically translates variables to fields and tags for the Influx-db in Line Protocol.  

    You can define *measurements* in **Measurements** page.

    - Check out available measurement and it's data:

        By default, there should be one measurement available. It should be compatible with your created entity ( from example above ) or the loaded entity by default if **DEMO** variable was set to **True** in **.env** file. 
        
        You can check this measurement data:

        - Navigate to **Measurements** page, **Get measurement information** tab.
        - Click the **dropdown** button below ```Measurement name```.
        - The available *measurement* should be loaded and seen as one of the options, if not there should be *"No measurements available."* line.
        - Click on the available measurement in the dropdown.
        - *Measurement* data should be loaded and displayed in the fields below.
        - If errors occur, notifications at the top-right of the screen should help to identify the problem.
<br>

- **Buckets:**

    Defining *buckets* is the second step to be able to use the module.

    *Bucket* defines where measurement will be placed. In a sense, *bucket* is a... bucket... a data sink, it can be filled with various data of various types. Then it can be quered, filtered and shaped into a more usable state to display in graphs. You can read more about buckets [here](https://docs.influxdata.com/influxdb/v2.0/organizations/buckets/).

    When Orion Context Broker subscription data is received and processed successfully, it searches if the *measurement* has valid *bucket* assigned.

    You can define *buckets* in **Buckets** page.

    - Check out available bucket and it's data:

        By default, there should be one bucket available. It should have assigned measurement already.
        
        You can check this bucket's data:

        - Navigate to **Buckets** page, **Get bucket information** tab.
        - Click the **dropdown** button below ```Bucket name```.
        - The available *bucket* should be loaded and seen as one of the options, if not there should be *"No buckets available."* line.
        - Click on the available *bucket* in the dropdown.
        - *Bucket* data should be loaded and displayed in the fields below.
        - If errors occur, notifications at the top-right of the screen should help to identify the problem.
<br>

- **Organizations:**

    Defining *organizations* is the third step to be able to use the module.

    *Organization* defines which workspace to use in Influx-db. An organization has seperate user groups, dashboards, tasks, buckets and etc. You can read more about organizations inside Influx-db [here](https://docs.influxdata.com/influxdb/v2.0/organizations/).  

    When Orion Context Broker subscription data is received and processed successfully and *measurement* had valid *bucket* assigned, then module tries to find *organization* that is assigned to the *bucket*.

    You can define *organizations* in **Organizations** page.

    - Check out available organization and it's data:

        By default, there should be one organization available. It should have assigned bucket already.
        
        You can check this organization's data:

        - Navigate to **Organizations** page, **Get organization information** tab.
        - Click the **dropdown** button below ```Organization name```.
        - The available *organization* should be loaded and seen as one of the options, if not there should be *"No organizations available."* line.
        - Click on the available *organization* in the dropdown.
        - *Organization* data should be loaded and displayed in the fields below.
        - If errors occur, notifications at the top-right of the screen should help to identify the problem.
<br>

- **Subscriptions:**

    Creating *subscriptions* is the last step to be able to use the module.

    *Subscriptions* are created inside Orion Context Broker are based on *measurements*. The subscriptions has triggers for entities and their properties. When entities change or get updated, subscriptions sends entity parameters to the defined end point. The end point in this case is this module. After processing the data received from subscription, the module uploads the data into Influx-db. More information about subscriptions can be found [here](https://telefonicaid.github.io/fiware-orion/api/v2/stable/) (in the Subscriptions reference). 

    When subscription is being created, information about desired entity and it's parameters are gathered from measurement automatically. If all of the data is valid and module was successful in creating the body of a subscription, then the module checks if other subscriptions were available for the desired measurement. The outcome of this check:
    - If no subscriptions were found - a new one is created.
    - If subscription was found - the old one is updated (overwritten).
    - If there were multiple subscriptions of the measurement - all of the duplicates will be deleted and new one will be created.
    <br>

    You can control *subscriptions* in **Subscriptions** page.

    - Create subscription for selected measurement:

        By default, there should be no subscriptions available, so you have to create it.
        
        To create subscription:

        - Navigate to **Subscriptions** page, **Subscribe to measurement** tab.
        - As subscriptions are based on *measurements*, you have to select the *measurement* to which you want to subscribe.
        - Click the **dropdown** button below ```Measurement name```.
        - The available *measurement* should be loaded and seen as one of the options, if not there should be *"No measurements available."* line.
        - Click on the available *measurement* in the dropdown.
        - The *dropdown* button text should be a *measurement* name.
        - Click the ```Subscribe``` button.
        - The *subscription* should be created and success notification will be displayed in the top-right corner of the screen.
        - If errors occur, notifications at the top-right of the screen should help to identify the problem.


    - Check out available subscription and it's data after creating it:

        By default, there should be no subscriptions available, so you have to create it.
        
        You can check your created subscription's data:

        - Navigate to **Subscriptions** page, **Show measurement subscription** tab.
        - As subscriptions are based on *measurements*, you have to select the *measurement* which subscription you want to see.
        - Click the **dropdown** button below ```Measurement name```.
        - The available *measurement* should be loaded and seen as one of the options, if not there should be *"No measurements available."* line.
        - Click on the available *measurement* in the dropdown.
        - *Subscription* data should be loaded and displayed in the field below. It should be a JSON like object.
        - If errors occur, notifications at the top-right of the screen should help to identify the problem.
<br>

### Influx-db:

- **Create *organizations* and *buckets*:**

    To test/try this module, the next step is to create **Organization** and **Bucket** inside your Influx-db server. 
    
    The name of the **Organization** and **Bucket** should be the same as used in the module, or the uploading of the data into Influx-db may fail. 
    
    If you have created a **Organization** and **Bucket** inside Influx-db already and want to use it, you can create it in the module and assign the *measurement*.

    :warning: By default ```docker-compose.yml``` file has defined first launch mode and variables used for setup. It will create default user, organization and bucket. The steps below can be different, if ```docker-compose.yml``` **influx-db** service was altered. You may need to set up Influx-db the first time you enter the page.

    - Creating organization and bucket inside Influx-db:

        - Navigate to Influx-db: ```<Your IP>:8086```
            - Example: ```http://192.168.0.50:8086```
        - Log-in to the Influx-db dashboard. 
            - If ```docker-compose.yml``` **Influx-db** service was changed - You may be greeted by first time setup page. In that case, fill all the required fields like in to ```Fill in the fields``` step below. Additionally choose your desired user ID and password.
            - If ```docker-compose.yml``` **Influx-db** service was unchanged - ID: ```admin```, PW: ```admin1234```
        - Navigate to new organization window.
            - Click on your user avatar in the navigation bar.
            - Then click ```Create organization``` in the pop-up.
            - or
            - Just go to ```http://<your_influxdb_address>/orgs/new```
                - Example: ```http://192.168.0.50/orgs/new```
        - Fill in the fields:
            - Organization name: ```Test```
                - If ```docker-compose.yml``` **Influx-db** service was unchanged: It should have been created.
            - Bucket name: ```Test```
                - If ```docker-compose.yml``` **Influx-db** service was unchanged: It should have been created.
        - Click ```Create```
    <br>
    
    You now should have the necessary **Organization** and **Bucket** inside of the Influx-db server.

### Testing the module:

The next step is to make updates to the entity that you created previously in the **Orion Context Broker.** part of this guide. This will trigger the subscriptions that you created in "**Using WEB interface.** **>Subscriptions**" part of this guide.

- Updating the entity of Orion Context Broker:

    - This can be done using one of the REST clients or tools that you installed in the [Installations steps](installationguide.md) or using curl requests in the terminal.
    - The request:
        - Path:
            - ```<Orion Context Broker IP>:1026/v2/entities/<Your entity ID>/attrs?options=keyValues```
        - Request type:
            - ```PATCH```
        - Request body:
            - JSON format.
            - Key, value pairs (with new values) that were defined when creating the entity.
    - Examples:

        - Example entity in almost any of the REST client/tool:

            ```<PATCH REQUEST> to 192.168.0.50:1026/v2/entities/hexapod1/attrs?options=keyValues```
            ``` 
            {
                "platform_x": 1,
                "platform_y": 2,
                "platform_z": 3
            }
            ```

        - Example using curl:

            ```
            curl 192.168.0.50:1026/v2/entities?options=keyValues -X PATCH -s -S -H 'Content-Type: application/json' -d @- <<EOF
            {
                "platform_x": 1,
                "platform_y": 2,
                "platform_z": 3
            }
            EOF
            ```

    :warning: Please change at least one **platform_*** value every time request is made. Othervise it won't be updated.
    :warning: One or all of the entity variables can be updated at a time.

Final step is to check out the results if the module actually did what it supposed to and uploaded data into **Influx-db**.

- **Explore Influx-db:**
    - Navigate to Influx-db: ```<Your IP>:8086```
        - Example: ```http://192.168.0.50:8086```
        <br>

    - Log-in to the Influx-db dashboard. 
        - If ```docker-compose.yml``` **Influx-db** service was unchanged - ID: ```admin```, PW: ```admin1234```
        <br>

    - Navigate to **Explore** page. Should be available on the navigation bar that is on the left of the screen.
    - :warning: Below ```Data explorer``` page header, change from ```Graph``` to ```Table``` visualization of the data.
    - Select appropriate time range in the ```Time input```, so the data would be available inside the range selected.
    - Click ```Script editor```.
    - In the **Editor** window, paste:

        ```
        from(bucket: "Test")
            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
            |> filter(fn: (r) => r["_measurement"] == "hexapod_position")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            |> keep(columns: ["_time", "_measurement", "hexapod", "x", "y", "z"])
            |> yield()
        ```

    - Click ```Submit```.
    - Data should be visible.
    - You can switch data visualization to ```Graph``` mode, to see changes overtime.
        - Replace **Editor** window text:

            ```
            from(bucket: "Test")
                |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                |> filter(fn: (r) => r["_measurement"] == "hexapod_position")
                |> yield()
            ```

    <br>
    
- No data visible
    - If no data is visible, please adjust time range to a wider scope.
    - If no data is still shown, replace **Editor** window text:

        ```
        from(bucket: "Test")
            |> range(start: -100y, stop: 100y)
            |> filter(fn: (r) => r["_measurement"] == "hexapod_position")
            |> yield()
        ```

    - If no data is still shown, replace **Editor** window text:

        :warning: Replace bucket and measurement name.

        ```
        from(bucket: <Your bucket>)
            |> range(start: -100y, stop: 100y)
            |> filter(fn: (r) => r["_measurement"] == <Your measurement name>)
            |> yield()
        ```

    - If no data is still shown:
    
        - Browse the logs in the terminal to figure out why and what crashed.
        - Browse logs in the ```FlexHex-Rose-AP/API/app/logs```, for the module logs to look for errors.
        - Go to [Trouble shooting](trouble-shooting.md) documentation page for known bugs.
    <br>
