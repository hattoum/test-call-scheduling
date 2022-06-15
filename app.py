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

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/uploads"
# jobs = []
scheduler = Scheduler()

# que = Queue()

# def get_jobs(scheduler):
#     jobs = scheduler.jobs
#     return jobs

@app.route("/", methods=["POST","GET"])
def index():
    # t = Thread(target=lambda q, arg1: q.put(get_jobs(arg1)), args=(que, scheduler))
    # t.start()
    # t.join()
    # jobs = que.get()
    jobs = scheduler.jobs
    print(jobs)
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
    scheduler.start()
    app.run(debug=True)