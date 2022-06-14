# %%
import ctypes
from time import sleep
from dataclasses import dataclass
from initial_entities import create_entities
from calls import *
import threading
import ctypes


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
        self.jobs = []
        self.daemon = True
    
    #Starts the timer    
    def run(self) -> None:
        while True:
            sleep(1)
            self.run_jobs()
            self.time +=1
          
    #Checks all current jobs to see if it is time to send a request    
    def run_jobs(self):
        for job in self.jobs:
            adjusted_time = self.time - job.start_time
            if adjusted_time%(job.call_interval*60) == 0 and adjusted_time != 0:
                job.call_count += 1
                self.send_request(job)
                
                #Remove job if it is done
                if job.call_count >= job.total_call_count:
                    self.remove_job(job)
                    
                #Refresh token every call_interval (10) calls
                if job.call_count % job.refresh_interval == 0 and job.call_count != 0:
                    refresh_token(job.username, job.password, job.auth_data)
    
    
    #Sends a POST request to create the calls                
    def send_request(self, job: Job) -> int:
        print(f"{job.name} is sending request")
        try:
            dialog = add_dialog(job.uuid, job.data, job.auth_data)
            if(dialog == 403):
                print("Account does not have permission to push calls")
            return dialog
        except:
            return 0
        
    
    #Remove job from list of jobs        
    def remove_job(self, job: Job):
        try:
            self.jobs.remove(job)
            return(f"{job.name} is done")
        except:
            return("Job not found")
        
    # returns a job given its name        
    def get_job_by_name(self, name: str) -> Job:
        for job in self.jobs:
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
        auth_data = refresh_token(job.username, job.password, job.auth_data)
        job.auth_data = auth_data
    
    #Creates a new job and adds it to the list of jobs        
    def create_job(self, job_name: str, username: str, password: str, call_count: int, call_interval: int, data_path: str, uuid: str) -> None:
        
        for job in self.jobs:
            if job.name == job_name:
                raise ValueError("Job already exists")
            
        data = create_entities(data_path)
        auth_data = get_auth(username, password)
        job = Job(job_name, username, password, call_count, call_interval, self.time, data, auth_data, uuid)
        code = self.send_request(job)
        if(code == 403):
            raise Exception("Account does not have permission to push calls")
        if(code == 0):
            raise Exception("Credentials are incorrect")

        self.jobs.append(job)
        return f"Job {job_name} created"
    
    
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

# def main(scheduler: Scheduler):
    
#     scheduler.start()
    
#     login = "hamer_api@voctiv.net"
#     password = "xATL6Qgh"
#     print(scheduler.create_job("one", login, password, 2, 1, "bb.xlsx","3c1221f6-cc53-476c-b70a-b09c232b8c65"))
#     sleep(30)
#     scheduler.create_job("one", login, password, 2, 1, "bbc.xlsx","3c1221f6-cc53-476c-b70a-b09c232b8c65")
#     while True:
#         sleep(0.1)
        
# if __name__ == "__main__":
#     scheduler = Scheduler()
#     try:
#         main(scheduler)
#     except KeyboardInterrupt:
#         scheduler.kill_thread()
    
