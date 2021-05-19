#!/bin/bash
cd $1
app_location=$1/../../API/app

/bin/python3 $1/../scripts/FindAndReplace.py $1/buckets.html assets static
/bin/python3 $1/../scripts/FindAndReplace.py $1/organizations.html assets static
/bin/python3 $1/../scripts/FindAndReplace.py $1/measurements.html assets static
/bin/python3 $1/../scripts/FindAndReplace.py $1/subscriptions.html assets static
/bin/python3 $1/../scripts/FindAndReplace.py $1/welcome.html assets static

cp buckets.html $app_location/templates/buckets.html
cp organizations.html $app_location/templates/organizations.html
cp measurements.html $app_location/templates/measurements.html
cp subscriptions.html $app_location/templates/subscriptions.html
cp welcome.html $app_location/templates/welcome.html
cp -R assets/* $app_location/static
