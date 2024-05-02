import functions_framework
import google.auth
from google.cloud import scheduler_v1
from datetime import datetime, timedelta
import random
import json

def adjust_time(current_time, delta_range, min_time, max_time):
    delta = random.randint(-delta_range, delta_range)
    adjusted_time = current_time + timedelta(minutes=delta)
    if adjusted_time < min_time:
        adjusted_time = min_time
    elif adjusted_time > max_time:
        adjusted_time = max_time
    return adjusted_time

def update_scheduler_job(job_name, project_id, region, schedule_time, delta_range, min_time, max_time):
    client = scheduler_v1.CloudSchedulerClient()
    job_path = client.job_path(project_id, region, job_name)
    job = client.get_job(name=job_path)

    current_time = datetime.strptime(schedule_time, '%H:%M')
    print(f'Current time: {current_time}')
    new_time = adjust_time(current_time, delta_range, min_time, max_time)
    print(f'New time: {new_time}')
    
    if (job_name == 'daily-task-friday'):
      job.schedule = new_time.strftime('%H %M * * 5')
    elif (job_name == 'daily-task-afternoon-mon-thu'):
      job.schedule = new_time.strftime('%H %M * * 1-4')
    else:
      job.schedule = new_time.strftime('%H %M * * 1-5')
    

    updated_job = client.update_job(job=job)
    print(f'Updated job: {updated_job.name}, Schedule: {job.schedule}')

@functions_framework.http
def adjust_scheduler_jobs(request):
    try:
        request_json = request.get_json()
        project_id = request_json['project_id']
        region = request_json['region']
        delta_range = 30  # Rango de 30 minutos para las variaciones

        min_morning = datetime.strptime("08:30", '%H:%M')
        max_morning = datetime.strptime("09:00", '%H:%M')

        min_afternoon_mon_thu = datetime.strptime("19:00", '%H:%M')
        max_afternoon_mon_thu = datetime.strptime("19:30", '%H:%M')

        min_afternoon_fri = datetime.strptime("16:45", '%H:%M')
        max_afternoon_fri = datetime.strptime("17:15", '%H:%M')

        jobs = [
            ('daily-task-morning', "09:00", min_morning, max_morning),
            ('daily-task-afternoon-mon-thu', "19:04", min_afternoon_mon_thu, max_afternoon_mon_thu),
            ('daily-task-friday', "16:47", min_afternoon_fri, max_afternoon_fri)
        ]

        for job_name, schedule_time, min_time, max_time in jobs:
            update_scheduler_job(job_name, project_id, region, schedule_time, delta_range, min_time, max_time)

        return json.dumps({'status': 'success'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)}), 500
