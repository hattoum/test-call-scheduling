from flask import Flask, redirect, render_template, url_for, request
from scheduler import Scheduler
import pandas as pd
import os
import gunicorn
from markupsafe import escape
from threading import Thread
from queue import Queue
import os
import redis
import pickle

try:
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    red = redis.from_url(redis_url)
    j = pickle.dumps([])
    red.set("jobs",j)
except:
    print("failed to connect to redis")


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/uploads"
scheduler = Scheduler()
scheduler.start()

@app.route("/", methods=["POST","GET"])
def index():
    try:
        jobs = pickle.loads(red.get("jobs"))
    except:
        jobs=[]
        print("No redis connection")
        
    template="index.html"
    if(request.method == "POST"):
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        uuid = request.form["uuid"]
        count = int(request.form["count"])
        interval = int(request.form["interval"])
        sheet = request.files["sheet"]
        
        
        try:
            scheduler.create_job(name, username, password, count, interval, sheet, uuid)
            return redirect(url_for("index"))
        except Exception as e:
            return render_template(template,jobs = jobs, message=str(e))
        
    
    else:
        return render_template(template,jobs= jobs, message="")
    
    
@app.route("/add", methods=["POST","GET"])
def add():

    if(request.method == "POST"):

        job = request.json["name"]
        scheduler.remove_job_by_name(job)
        
        return "200"


    