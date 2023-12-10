# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the dates and precipitation from the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precip_data = {date: prcp for date, prcp in results}

    # Return the JSON representation of your dictionary
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query for the stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    stations = list(np.ravel(results))

    # Return a JSON list of stations from the dataset
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the dates and temperature observations from the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list
    tobs = list(np.ravel(results))

    # Return a JSON list of Temperature Observations (tobs) for the previous year
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # Convert the start date from string to date format
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400
    
    # Query for the minimum, maximum, and average temperatures from the start date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a list
    start_temps = list(np.ravel(results))

    # Return a JSON list of the minimum, maximum, and average temperatures
    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Convert the start and end dates from string to date format
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400

    # Query for the minimum, maximum, and average temperatures for a given start-end range
    results = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(
        Measurement.date >= start_date,
        Measurement.date <= end_date
    ).all()

    # Convert the query results to a list
    start_end_temps = list(np.ravel(results))

    # Return a JSON list of the minimum, maximum, and average temperatures for a given start-end range
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)
    
    