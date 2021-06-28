# FlexHex ROSE-AP

[![License: Apache 2.0](https://img.shields.io/github/license/Factobotics/FlexHex-Rose-AP)](https://opensource.org/licenses/Apache-2.0)
<br/>
[![Documentation Status](https://readthedocs.org/projects/flexhex_rose-ap/badge/?version=latest)](https://flexhex_rose-ap.readthedocs.io/en/latest/?badge=latest)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4952/badge)](https://bestpractices.coreinfrastructure.org/projects/4952)

ROSE-AP of the FlexHex project tries to make data gathering from Orion Context Broker entities to influx-db easier.

This project is part of [DIH^2](http://www.dih-squared.eu/). For more information check the RAMP Catalogue entry for the
[components](https://github.com/ramp-eu).


## Contents

-   [Background](#background)
-   [Installation guide](#installation-guide)
-   [Quickstart and step-by-step guides](#quickstart-and-step-by-step-guides)
-   [API](#api-guide)
-   [Testing](#testing)
-   [License](#license)

## Background

Data gathering can be cumbersome sometimes. This module tries to solve and simplify it. To make data gathering to influx-db a bit easier.

It tries to do so via WEB interface and for more advanced use cases - API.

Currently there are four main parts that user/operator can control:

- Measurements - Measurement to be processed from incoming Orion Context Broker subscription data and uploaded into influx-db. User defines entities and their types for the Orion Context Broker subscription. Also fields and tags to gather from the Orion Context Broker entity.
- Buckets - Used to define buckets of the influx-db. Allows to assign different measurements.
- Organizations -  Used to define organizations of the influx-db. Allows to assign different buckets.
- Subscriptions - Used to control selected measurement subscription. [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) (Create, read, update and delete) principle. Main use case - automatically form the required subscription for the selected measurement and post it to Orion Context Broker.

It is based on Orion Context Broker entities and subscriptions, and is NGSIv2 compliant to process the incoming data into Line Protocol for influx-db.

## Architecture

Information about architecture of the FlexHex ROSE-AP can be found in the [Architecture documentation](architecture.md).


## Installation guide

How to install the component

Information about how to install the FlexHex ROSE-AP can be found at the corresponding section of the
[Installation & Administration Guide](installationguide.md).

## Quickstart and step-by-step guides

How to use the component

Information about how to get started using the FlexHex ROSE-AP can be found in the [Getting Started guide](getting-started.md).

Information about how to use the FlexHex ROSE-AP can be found in the [Step-by-step guide](step-by-step.md).

## API guide

Information about the API of the FlexHex ROSE-AP can be found in the [API documentation](api.md).


## Testing

For now, API tests are available. 

They are done using python module "[pytest](https://docs.pytest.org/en/latest/)" and for coverage "[coverage](https://coverage.readthedocs.io/en/latest/)".

To install the modules, you need Python 3. Python3.7+ recommended. You can get python [here](https://www.python.org/downloads/). Also, python packet manager **pip** is required.

### Installing dependencies

Installing **pytest** and **coverage**:

- ```pip3 install pytest```

- ```pip3 install coverage```

### Running tests

:warning: To run tests, ROSE-AP dependencies has to be running. For now, they are not being mocked/simulated. To make it work, run  projects ```docker-compose```.

:warning: To run tests, change ```FlexHex-Rose-AP/API/app/.env``` file IP addresses to your machine IP address.

#### Running pytest

Navigate to app directory inside terminal or open terminal in the directory:

- ```cd FlexHex-Rose-AP/API/app```

Run **pytest**:

- ```pytest```

    It will gather all tests available and it will run them. All of the tests are currently inside ```FlexHex-Rose-AP/API/app/test_main.py``` module.

    After few moments, there should be logs appearing with the status of tests and finally the result will be displayed if everything was successful or not and why.

#### Running coverage

Navigate to app directory inside terminal or open terminal in the directory:

- ```cd FlexHex-Rose-AP/API/app```

Run **coverage**:

- ```coverage run -m pytest```

    Coverage will run **pytest** and it will collect metrics in the background.

Get **coverage** report:

:warning: Run this only after the "Run **coverage**" step.

- ```coverage report```

    It will display a table representing statements in files and how many of those statements are not covered by tests and the coverage of tests in percentage.


Get **coverage** report in a HTML file:

:warning: Run this only after the "Run **coverage**" step.

- ```coverage html```

    This will create ```htmlcov``` directory inside ```FlexHex-Rose-AP/API/app```. Inside, locate and open ```index.html``` in your browser. 

    If everything was successful, there should be interactive report that will display lines where tests don't cover statements, percentage of coverage, excluded statements.


## License

[Apache 2.0](LICENSE) © Factobotics
