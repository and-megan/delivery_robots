## About
This is an app with models and an API. 
Stations can be created, read, updated, and destroyed. Stations are created with a latitude and longtitude. 
A station's latitude and/or lontitude can be updated.

Drones (boats) can be created, read, updated, and destroyed. Drones are created to be at either a station or on a route.
A drone can change routes or stations.

Routes can be created, read, updated, and destroyed. Routes are created with a list/array of latitude and longitude points.
A route's path can be updated.

This is a Flask app using the Flask-RESTful extension for some boilerplate code to support the REST API.
I chose Flask as it is a lightweight, quick to spin up web framework for Python. Flask-RESTful was chosen because of its
guidance for a RESTful API and some boilerplate code.

The database is PostgreSQL with the PostGIS extension in order to lend support of geographic objects and calculations.
After researching, it seemed PostGIS was a good way to calculate distance spheres on Earth. Rather than importing packages
or trying to reinvent the wheel, I wanted to use a trusted method to handle geometry features.
Marshmallow is used to validate, serialize, and deserialize data from the API layer. This was done to reduce the amount 
of custom validation needed for data submitted to the API as well as an easy way to dump data to respond to API requests.

I chose to write unit tests for the models and resources exposed to the API. DroneRoutes exist only to tie together time, 
drones, and routes and are not interacted with directly.

This project was created using Python 3.7.4

### How to run
1. `pip install -r requirements.txt`
2. Run `flask migrate`
3. run `export FLASK_APP=main.py` in the command line at the root directory
4. `flask run` starts the app
5. `flask shell` starts the shell 
6. API instructions are below
7. Run tests with `pytest app/tests/...`
  

## API
ALL: ids are integers

Base API URL in development: `http://127.0.0.1:5000`

### Drone
##### GET `/api/v1.0/drones/:id`
get a drone

##### GET `/api/v1.0/drones/`
get all drones

##### POST `/api/v1.0/drones/`
create a drone
- required args: one of `station_id` (int) OR `route_id` (int)

##### PUT `/api/v1.0/drones/:id`
update a drone
- required args: one of `station_id` (int) OR `route_id` (int)

##### DELETE `/api/v1.0/drones/:id`
delete a drone


### Route
##### GET `/api/v1.0/routes/:id`
get a route

##### GET `/api/v1.0/routes/`
get all routes

Optional: 
- To get the route for a drone at a timestamp, pass `drone_id` (required) and `target_ts` (Unix timestamp, required) in the query string.
- To get the route for a drone at a timestamp, pass `drone_id` (required), `start_ts` (Unix timestamp, optional), `end_ts` (Unix timestamp, optional) in the query string.
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

##### DELETE `/api/v1.0/drones/:id`
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
- Drones do not need any guidance when are moved on routes or to stations, i.e. not creating routes between current location and next location
- Users will input longitude & latitude points as specified in the README API notes
