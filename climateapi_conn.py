
# imports

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
# import ipdb;ipdb.set_trace()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


app = Flask(__name__)

# app routes

app.config["JSON_SORT_KEYS"] = False

#home for the results to show
@app.route("/")
def index():
    return (
        f"+++++++++++++++++++++++++<br>"
        f".........................<br>"
        f"Weather API:<br>"
        f".........................<br>"
        f"+++++++++++++++++++++++++<br>"
        f"Precipitation for last year: /api/v1.0/precipitation<br/>"
        f"____________________________________________________<br/>"
        f"List of all stations: /api/v1.0/stations<br/>"
        f"____________________________________________________<br/>"
        f"Date and temperature observations from the last year: /api/v1.0/tobs<br/>"
        f"____________________________________________________<br/>"        
        f"Min, Avg, Max Temp given a start date up to most current date in db: /api/v1.0/<start><br/>"
        f"_____________________________________________________<br/>"
        f"Min, Avg, Max Temp given a start and end date: /api/v1.0/2015-09-12/2015-09-13<br/>"
        f"______________________________________________________<br/>"
    )

# Precipitation for last year
@app.route("/api/v1.0/precipitation")  

def precip():
    prcpquery = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-22').\
    filter(Measurement.date <= '2017-08-23').\
    order_by(Measurement.date)
    
    prcpdata = []
    for rain in prcpquery:
        prcp_dict = {}
        prcp_dict['date'] = rain.date
        prcp_dict['prcp'] = rain.prcp
        prcpdata.append(prcp_dict)

    return jsonify(prcpdata)  

# List of all stations

@app.route("/api/v1.0/stations")
def stations():
    #query for the data, practicing join even though station table has both columns queried below
    stations = session.query(Station.name, Measurement.station)\
    .filter(Station.station == Measurement.station)\
    .group_by(Station.name).all()

    stations_data = []
    for station in stations:
        stat_dict = {}
        stat_dict['name']    = station.name
        stat_dict['station'] = station.station
        stations_data.append(stat_dict)
    
    return jsonify(stations_data)

# Date and temperature observations from the last year
@app.route("/api/v1.0/tobs")

def tobs():
    tobsquery = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= '2016-08-22').\
    filter(Measurement.date <= '2017-08-23').\
    order_by(Measurement.date)

    tobsdata = []
    for tobs in tobsquery:
        tobs_dict = {}
        tobs_dict['date'] = tobs.date
        tobs_dict['tobs'] = tobs.tobs
        tobsdata.append(tobs_dict)
    
    return jsonify(tobsdata)

# Temp given a start date to the most recent date
@app.route("/api/v1.0/<start>")
def trip1(start):

    trip = session.query\
    (func.min(Measurement.tobs).label('min'),\
    func.avg(Measurement.tobs).label('avg'),\
    func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= start).all()
    

    trip_list = []
    for t in trip:
        trip_dict = {}
        trip_dict['Start Date'] = start
        trip_dict['Min Temp'] = t.min
        trip_dict['Avg Temp'] = t.avg
        trip_dict['Max Temp'] = t.max
        trip_list.append(trip_dict)
    
    return jsonify(trip_list)


# Min, Avg, Max Temp given a start and end date

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
 
    trip_data = session.query(func.min(Measurement.tobs).label('min'),\
    func.avg(Measurement.tobs).label('avg'),\
    func.max(Measurement.tobs).label('max'))\
    .filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()

    data = []
    for t in trip_data:
        data_dict = {}
        data_dict['StartDate'] = start
        data_dict['EndDate'] = end
        data_dict['MinTemp'] = t.min
        data_dict['AvgTemp'] = t.avg
        data_dict['MaxTemp'] = t.max
        data.append(data_dict)
    
    return jsonify(data)

  
# closing

if __name__ == '__main__':
    app.run(debug=True)
