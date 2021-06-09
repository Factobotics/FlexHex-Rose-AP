# Getting started guide

## Contents

-   [Install](#install-the-components-and-get-project-files)
-   [Run docker](#running-docker-compose)
-   [Using the module UI](#using-the-module-ui-create-subscription-for-demo-measurement)
-   [Updating Orion Context Broker entity](#update-demo-entity)
-   [Query and see data inside Influx-db](#see-the-results-in-influx-db)

## Install the components and get project files

- Complete the [installation guide](installationguide.md).

## Running docker-compose.

- Open terminal
    - Linux users: **```CTRL + SHIFT + T```**
    - Windows users: **```Windows key + X```** and then press **A** key.
    <br>
- Navigate to **rose-ap** folder.

    ```cd rose-ap```

- Launch the docker compose:

    ```docker-compose up --build```  
    
- It can take some time for all of the images to be pulled from the internet and then built, so please be patient. It can take up to 5 minutes on 100MB/s internet.

## Using the module UI. Create subscription for demo measurement

- Navigate to **Subscriptions** page.
    - ```http://<your IP address>:5000/subscriptions```
    - Or use navbar on the left of the page ```http://<Your IP address>:5000```
- Navigate to **Subscribe to measurement** tab.
- Click on the *dropdown* below *Measurement name*.
- Select the **hexapod_position** demo measurement.
- Click **Subscribe**.
- The *subscription* should be created and success notification will be displayed in the top-right corner of the screen.
- If errors occur, notifications at the top-right of the screen should help to identify the problem.

## Update demo entity

- Pick one of your prefered *REST Client* or one of the tools from the list in [installation guide](installationguide.md) **REST clients**.
- Make a **PATCH** request to update Orion Context Broker entity.
    You will be updating the **hexapod1** entity, that is created by default when system starts.

    - Address:

        - ```http://<Your IP address>:1026/v2/entities/hexapod1/attrs?options=keyValues```

    - Request type:

        - ```PATCH```

    - Request body:
        - Content-Type: application/json
        - Body:
        
            ```
            {
                "platform_x": 1,
                "platform_y": 2,
                "platform_z": 3
            }
            ```

    :warning: Patch demo entity a few times, but everytime change at least one of the "platform_" values. So the "coordinates" would change, otherwise, the Orion Context Broker may ignore duplicates. 

## See the results in Influx-db

- Navigate to Influx-db user interface.
    - Address:
        - ```http://<your IP address>:8086/``` 
- Navigate to Explore tab (via navigation bar on the left).
- In the **FROM** column select "Test" bucket.
- In the **Filter** > **_measurement** column select **"hexapod_position"** measurement.
- In the right bottom corner of the page, select **Aggregate function** > **last**.
- Click the **Submit** button.
- It should display a graph. Data points on the graph depends on the amount of patch requests/updates made to the demo entity.

Alternative:

- Navigate to Influx-db user interface.

    - Address:

        - ```http://<your IP address>:8086/``` 

- Navigate to Explore tab (via navigation bar on the left).
- Switch to **Script editor** mode. (button near *Submit*)
- Paste the query:

    ```
    from(bucket: "Test")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "hexapod_position")
    ```
    
- Click the **Submit** button.
- It should display a graph. Data points on the graph depends on the amount of patch requests/updates made to the demo entity.

Troubleshooting:

- If only one data point is present, there will be no graph displayed, better to switch to table view. (Dropdown under *Data explorer* at the top of the page)

- If there is no data visible at all:
    - Increase time range in the dropdown.
    - Switch view to *table*. (Dropdown under *Data explorer* at the top of the page)
