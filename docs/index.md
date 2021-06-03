# FlexHex ROSE-AP

[![License: Apache 2.0](https://img.shields.io/github/license/Factobotics/FlexHex-Rose-AP)](https://opensource.org/licenses/Apache-2.0)
<br/>
[![Documentation Status](https://readthedocs.org/projects/flexhex_rose-ap/badge/?version=latest)](https://flexhex_rose-ap.readthedocs.io/en/latest/?badge=latest)

ROSE-AP of the FlexHex project tries to make data gathering from Orion Context Broker entities to influx-db easier.

This project is part of [DIH^2](http://www.dih-squared.eu/). For more information check the RAMP Catalogue entry for the
[components](https://github.com/ramp-eu).

| :books: [Documentation](https://flexhex_rose-ap.readthedocs.io/en/latest/) |
| --------------------------------------------- |


## Contents

-   [Background](#background)
-   [Install](#install)
-   [Usage](#usage)
-   [API](#api)
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

## Quickstart and step-by-step guide

How to use the component

Information about how to get started using the FlexHex ROSE-AP can be found in the [Getting Started guide](getting-started.md).

Information about how to use the FlexHex ROSE-AP can be found in the [Step-by-step guide](step-by-step.md).

## API guide

Information about the API of the FlexHex ROSE-AP can be found in the [API documentation](api.md).


## Testing

TBD

## License

[Apache 2.0](LICENSE) © Factobotics
