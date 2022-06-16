# %%
import ctypes
from time import sleep
from dataclasses import dataclass
from initial_entities import create_entities
import calls
import threading
import ctypes
import redis
import os
import pickle
import inspect
import threading
from datetime import datetime

@dataclass
class Job:
    name: str
    username: str
    password: str
    total_call_count: int
    call_interval: int
    start_time: int
    data: str
    auth_data: dict
    uuid: str
    call_count: int = 1
    refresh_interval: int = 10  

class Scheduler(threading.Thread):
    def __init__(self) -> None:
        threading.Thread.__init__(self)
        self.time = 0
        self.daemon = True
        self.redis = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))

    
    #Starts the timer    
    def run(self) -> None:
        while True:
            sleep(1)
            self.run_jobs()
            self.time +=1
          
    #Checks all current jobs to see if it is time to send a request    
    def run_jobs(self):
        jobs = self.get_unpickled()
        for job in jobs:
            adjusted_time = self.time - job.start_time
            if adjusted_time%(job.call_interval*60) == 0 and adjusted_time != 0:
                job.call_count += 1
                self.send_request(job)
                #Remove job if it is done
                if job.call_count >= job.total_call_count:
                    self.remove_job(job)
                    
                #Refresh token every call_interval (10) calls
                if  job.call_count % job.refresh_interval == 0 and job.call_count != 0:
                    self.refresh_token(job)
                    
                self.send_pickle(jobs)
    
    
    #Sends a POST request to create the calls                
    def send_request(self, job: Job) -> int:
        print(f"{job.name} is sending request")
        try:
            dialog = calls.add_dialog(job.uuid, job.data, job.auth_data)
            if(dialog == 403):
                print("Account does not have permission to push calls")
            return dialog
        except:
            return 0
        
    
    #Remove job from list of jobs        
    def remove_job(self, job: Job):
        try:
            jobs = self.get_unpickled()
            jobs.remove(job)
            self.send_pickle(jobs)
            print(f"{job.name} has been removed")
            print(f"# active jobs: {len(jobs)}")
            return(f"{job.name} is done")
        except:
            return("Job not found")
        
    # returns a job given its name        
    def get_job_by_name(self, name: str) -> Job:
        jobs = self.get_unpickled()
        for job in jobs:
            if job.name == name:
                return job
        return None
    
    #Removes a job from the list of jobs by name
    def remove_job_by_name(self, name: str) -> str:
            try:
                job = self.get_job_by_name(name)
                self.remove_job(job)
                return f"{name} is done"
            except:
                return "Job not found"
            
    def refresh_token(self, job: Job):
        try:
            auth_data = calls.refresh_token(job.username, job.password, job.auth_data)

            
            job.auth_data = auth_data
        except:
            print(f"{job.name} failed to refresh token")
            raise Exception("Failed to refresh token")
    
    #Creates a new job and adds it to the list of jobs        
    def create_job(self, job_name: str, username: str, password: str, call_count: int, call_interval: int, data_path: str, uuid: str) -> None:

        jobs = self.get_unpickled()
        
        for job in jobs:
            if job.name == job_name:
                raise ValueError("Job already exists")
            
        data = create_entities(data_path)
        auth_data = calls.get_auth(username, password)
        
        if "message" in auth_data:
            raise Exception("Failed to get auth token, try again")
        
        job = Job(job_name, username, password, call_count, call_interval, self.time, data, auth_data, uuid)
        code = self.send_request(job)
        if(code != 200 and code != 200):
            if(code == 403):
                raise Exception("Account does not have permission to push calls")
            elif(code == 0):
                raise Exception("Credentials are incorrect")
            elif(code == 400):
                raise Exception("UUID is incorrect")
            else:
                print(code)
                raise Exception(f"Error code {code}")
        
        jobs.append(job)
        
        try:
            self.send_pickle(jobs)
            return f"Job {job_name} created"
        except:
            raise Exception("Failed to send pickle")
        
    
    # returns id of the thread the object is running in    
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
            
    #Forcibly terminates thread    
    def kill_thread(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            
            
    def get_unpickled(self):
        unpickled_jobs = pickle.loads(self.redis.get("jobs"))
        return unpickled_jobs

    def send_pickle(self, jobs):
        pickled_jobs = pickle.dumps(jobs)
        self.redis.set("jobs", pickled_jobs)


