# Delivery Robots
Note currently in the process of doing a couple of upgrades and running into a few issues.... Standby for a fully functional app.

## About
This is an app for handling your fleet of delivery robots! Is your robot supposed to deliver a New York style slice of pizza to Chicago? Is another robot delivering a time sensitive file from Buenos Aires to Barcelona?

Robots need charging, or docking, stations in order to recharge on their long journeys.

This is an app with models and an API.
DockingStations can be created, read, updated, and destroyed. DockingStations are created with a latitude and longtitude.

Robots (delivery drones) can be created, read, updated, and destroyed. Robots are created either at a DockingStation or on a Route.
A robot can change routes or docking stations.

Routes can be created, read, updated, and destroyed. Routes are created with a list/array of latitude and longitude points.
A route's path can be updated.

This is a Flask app using the Flask-RESTful extension for some boilerplate code to support the REST API.
I chose Flask as it is a lightweight, quick to spin up web framework for Python. Flask-RESTful was chosen because of its guidance for a RESTful API and some boilerplate code. It also has a lot of community support. There are some interesting frameworks like FastAPI that may be explored in future to port this API over ot.

The database is PostgreSQL with the PostGIS extension in order to lend support of geographic objects and calculations. PostGIS is a great way to calculate distance spheres on Earth. Rather than importing packages
or trying to reinvent the wheel, I use a widely trusted method to handle geometry features.

Marshmallow is used to validate, serialize, and deserialize data from the API layer. This reduces the amount of custom validation needed for data submitted to the API. It's also an easy way to dump data to respond to API requests.

I chose to write unit tests for the models and resources exposed to the API. RobotRoutes exist only to tie together time, robotos, and routes. RobotRoutes are not interacted with directly.

This project was created using Python 3.7.4

### How to run
1. Run postgres locally and create two dbs - delivery_db, delivery_test_db
1a. install postgis `CREATE EXTENSION postgis;`
2. `cd delivery_robots/`
3. Create virtual environment & run `pip install -r requirements.txt`
4. Run `export FLASK_APP=robots/main.py` in the command line at the root directory
5. Run `flask db upgrade`
6. `flask run` starts the app
7. `flask shell` starts the shell
8. API instructions are below
9. Run tests with `pytest app/tests/...`


## API
ALL: ids are integers

Base API URL in development: `http://127.0.0.1:5000`

### Robot
##### GET `/api/v1.0/robots/:id`
get a robot

##### GET `/api/v1.0/robots/`
get all robots

##### POST `/api/v1.0/robots/`
create a Robot
- required args: one of `station_id` (int) OR `route_id` (int)

##### PUT `/api/v1.0/Robots/:id`
update a Robot
- required args: one of `station_id` (int) OR `route_id` (int)

##### DELETE `/api/v1.0/Robots/:id`
delete a Robot


### Route
##### GET `/api/v1.0/routes/:id`
get a route

##### GET `/api/v1.0/routes/`
get all routes

Optional:
- To get the route for a robot at a timestamp, pass `robot_id` (required) and `target_ts` (Unix timestamp, required) in the query string.
- To get the route for a robot at a timestamp, pass `robot_id` (required), `start_ts` (Unix timestamp, optional), `end_ts` (Unix timestamp, optional) in the query string.
- default of `start_ts` is epoch
- default of `end_ts` is current time

##### POST `/api/v1.0/routes/`
create a route
- required args: `points` as an array of arrays of longitude and latitude
- example: `[[-122.3462, 37.8770], [-122.4599, 36.8770]] # [[longitude, latitude], [longitude, latitude]]`
- length of points must be greater than or equal to 2

##### PUT `/api/v1.0/routes/:id`
update a route
- required args: `points` as an array of arrays of longitude and latitude floats
- example: `[[-122.3462, 37.8770], [-122.4599, 36.8770]] # [[longitude, latitude], [longitude, latitude]]`
- length of points must be greater than or equal to 2

##### DELETE `/api/v1.0/robots/:id`
delete a route


### Station
##### GET `/api/v1.0/stations/:id`
get a station

##### GET `/api/v1.0/stations/`
get all stations

Optional:
- To get all stations within a radius of a target point, pass `radius` (in NM as an integer), `target_longitude` (float), and `target_latitude` (float) in the query string.
- To get all stations within a radius of a target route, pass `radius` (in NM as an integer) and `route_id` in the query string.

##### POST `/api/v1.0/stations/`
create a station
- required args: `longitude` (float) AND `latitude` (float)

##### PUT `/api/v1.0/stations/:id`
update a station

- required args: `longitude` (float) and/or `latitude` (float)

##### DELETE `/api/v1.0/stations/:id`
delete a station


### Assumptions
- All latitude and longitude points given will be on an ocean
- Any changes to Route paths are acceptable, i.e. not validating route changes
- Robots do not need any guidance when are moved on routes or to stations, i.e. not creating routes between current location and next location
- Users will input longitude & latitude points as specified in the README API notes
