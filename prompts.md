## May 13, 2025
My task is to create a series of services that simulate temperature data generators, electricity usage, humidity etc.

I should have a consumer that stores this to the influxdb database.

I should also have a graphQL ui to view the data once it is stored.

This should be made from the docker-compose file and the services should be added to this compose file as well. Make the docker files necessary and the python files necessary to run the services.

Errors:
2025-05-13 13:57:47,098 - consumer - INFO - Received message: {'sensorId': 'temp_003', 'sensorType': 'temperature', 'location': 'Bedroom', 'value': 20.05, 'unit': '°C', 'timestamp': '2025-05-13T13:57:47.095996Z'}
2025-05-13 13:57:47,098 - consumer - ERROR - Error storing data: (401)
Reason: Unauthorized
HTTP response headers: HTTPHeaderDict({'Content-Type': 'application/json; charset=utf-8', 'X-Influxdb-Build': 'OSS', 'X-Influxdb-Version': 'v2.7.11', 'X-Platform-Error-Code': 'unauthorized', 'Date': 'Tue, 13 May 2025 13:57:47 GMT', 'Content-Length': '55'})
HTTP response body: {"code":"unauthorized","message":"unauthorized access"}

ts=2025-05-13T13:57:47.098561Z lvl=info msg=Unauthorized log_id=0wUUlR5W000 error="authorization not found"


## May 14, 2025

(on aggregator.go)
This file aggregates the values found within the given measurement into min max and sum. However, there is a misunderstanding. The data we are querying on have measurements in the format like the one in sensordata and that is inserted in dataconsumer. These are the values we want to aggreagte, and preferably one aggregation per sensor in a location, as well as per sensortype. Can you make this? Split the aggregation task into seperate files, one per sensortype. humidity, electricity and temperature. Do this even if the files get very small