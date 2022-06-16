from flask import Flask, redirect, render_template, url_for, request, jsonify
from scheduler import Scheduler
import codecs
import pandas as pd
import os
from time import sleep
import json
import gunicorn
from markupsafe import escape
from threading import Thread
from queue import Queue
import os
import redis
from redisworks import Root
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
scheduler = Scheduler("test")
# scheduler.start()
t = Thread(target=scheduler.run, daemon=True)
t.start()

@app.route("/", methods=["POST","GET"])
def index():
    try:
        jobs = pickle.loads(red.get("jobs"))
        # print(jobs)
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
        
        # print(type(request.json["name"]))
        job = request.json["name"]
        scheduler.remove_job_by_name(job)
        # return render_template("index.html",jobs=scheduler.jobs, status = "")
        
        return "200"

if __name__ == "__main__":
    print("how")
    app.run(debug=False)

    