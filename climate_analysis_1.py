#Import packages 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite",
                       connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#Initial Welcome page in flask displaying the route options
#for different types of information
@app.route("/")
def welcome():
    """List all available api routes."""
    return"""<html>
    <h1>List of all available Hawaii API routes</h1>
    <ul>
        <br>
            <li>
            Return a list of precipation from last year:
            <br>
                <a href = "/api/v1.0/precipitation">/api/v1.0/precipitation</a>
            </li>
            <br>
            <li>
            Return a list of stations:
            <br>
                <a href = "/api/v1.0/stations">/api/v1.0/stations</a>
            </li>
            <br>
            <li>
            Return a list of Temperature Observations:
            <br>
                <a href = "/api/v1.0/tobs">/api/v1.0/tobs</a>
            </li>
            <br>
            <li>
            Return a list of of min, max, avg for the dates provided:
                
                <br>Replace &ltstart&gt with date in Year_Month_Day format
                <br>
                    <a href = "/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a>
                    

            </li>
            <br>
            <li>
            Return a list of of min, max, avg for the dates in range of start and end dates:
                
                <br>Replace &ltstart&gt with date in Year_Month_Day format
                <br>
                    <a href = "/api/v1.0/2017-01-01/2017-03-01">/api/v1.0/2017-01-01/2017-03-01</a>
            </li>
            <br>
    </ul>
</html>
"""

#Setting the precipiation route that shows the precipiation for last year
#
@app.route("/api/v1.0/precipitation")
def precipiation():
    """Return a list of precipitation from last year"""
    # Query all date from Measurement table and sort in desc order to get the most recent date
    # in the table
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Get the most recent date in the session
    max_date = max_date[0]
    # Use the timedelta as the place holder to subtract the result from the query to 
    # get a list of values in a year timeframe
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Query Measurement table for date and precipitiation using for a single year
    prec_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    # Put the results in a dict to present in local site
    results = dict(prec_results)

    return jsonify(results)

# Route for stations
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations from Measurement table
    station = session.query(Measurement.station).group_by(Measurement.station).all()
    # Use np.ravel() to flatten the array to put into a list
    station_list = list(np.ravel(station))


    return jsonify(station_list)

# Route for Temperature information for a year
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of Temperature Observations for previous year"""
    # Query all dates from Measurement table
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Retrieve the most recent date in the table
    max_date = max_date[0]
    # Use dt.timedelta to get a year of data
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Retrieve the date and temperatures from Measurement tables for the year
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    # Put data into a list 
    tobs_list = list(tobs)


    return jsonify(tobs_list)


# Route for min, max, and avg from a start date to the last date in the data
@app.route("/api/v1.0/<start>")
def start(start = None):
    """Return a list of min, max, avg for dates greater than start"""
    # Query for the min, max, and avg from the start date which is declared gy the link which is initialized
    # but can be changed directly on the link to change the query parameters 
    start_date = session.query(Measurement.date, func.min(Measurement.tobs),func.avg(Measurement.tobs),\
                   func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

    start_date_list = list(start_date)


    return jsonify(start_date_list)

# Route for, min, max, and avg for start and end dates
@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end = None):
    """Return a list of min, max, avg for dates between start and end"""
    # Query for the min, max, and avg from the start date and end date
    # which is declared gy the link which is initialized but can be changed directly on the link 
    # to change the query parameters
    between = session.query(Measurement.date, func.min(Measurement.tobs),func.avg(Measurement.tobs),\
                   func.max(Measurement.tobs)).filter(Measurement.date >= start)\
                    .filter(Measurement.date <= end).group_by(Measurement.date).all()

    between_date = list(between)


    return jsonify(between_date)


if __name__ == '__main__':
    app.run(debug=True)
