from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
import pandas as pd

engine  = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)



app = Flask(__name__)
@app.route("/")
def Home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(recent, "%Y-%m-%d") - dt.timedelta(days = 365)
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    return jsonify(prcp_results)

@app.route("/api/v1.0/stations")
def stations():
    session  = Session(engine)
    stations_results = session.query(Station.station, Station.name).all()
    return jsonify(stations_results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(recent, "%Y-%m-%d") - dt.timedelta(days = 365)
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active = station_counts[0][0]
    tobs_data = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.station == most_active).order_by(Measurement.date).all()
    return jsonify(tobs_data)
    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start(start = 'none', end = 'none'):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)        

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
  
    return jsonify(results)


if __name__ == '__main__':
    app.run()
