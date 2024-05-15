import functions_framework
import google.auth
from google.cloud import scheduler_v1
from datetime import datetime, timedelta
import random
import json

def adjust_time(current_time, delta_range, min_time, max_time):
    # Calcula el rango de minutos hasta el máximo y hasta el mínimo
    max_minutes = int((max_time - current_time).total_seconds() / 60)
    min_minutes = int((min_time - current_time).total_seconds() / 60)

    # Genera un delta aleatorio con una distribución sesgada hacia el rango, menos hacia el máximo
    if random.random() < 0.99:  # 99% de probabilidad de estar en el rango general
        delta = random.randint(min_minutes, max_minutes - 1)
    else:  # 1% de probabilidad de tocar exactamente el máximo
        delta = max_minutes

    # Calcula el tiempo ajustado
    adjusted_time = current_time + timedelta(minutes=delta)

    return adjusted_time


def update_scheduler_job(job_name, project_id, region, schedule_time, delta_range, min_time, max_time, fixed_time=None):
    client = scheduler_v1.CloudSchedulerClient()
    job_path = client.job_path(project_id, region, job_name)
    job = client.get_job(name=job_path)

    if fixed_time:
        new_time = fixed_time
    else:
        current_time = datetime.strptime(schedule_time, '%H:%M')
        print(f'Current time: {current_time}')
        new_time = adjust_time(current_time, delta_range, min_time, max_time)
        print(f'New time: {new_time}')

    # Ajusta las cadenas cron asegurándote de que sean válidas
    # if job_name == 'daily-task-friday' or job_name == 'daily-task-friday-api':
    if job_name == 'daily-task-friday':
        job.schedule = new_time.strftime('%M %H * * 5')
    elif job_name == 'daily-task-afternoon-mon-thu':
    #elif job_name == 'daily-task-afternoon-mon-thu' or job_name == 'daily-task-afternoon-mon-thu-api':
        job.schedule = new_time.strftime('%M %H * * 1-4')
    else:
        job.schedule = new_time.strftime('%M %H * * 1-5')

    # Asegúrate de que la zona horaria sea válida
    job.time_zone = 'America/Santiago'  # Ajusta según tu zona horaria

    updated_job = client.update_job(job=job)
    print(f'Updated job: {updated_job.name}, Schedule: {job.schedule}')

    # Devuelve el tiempo actualizado
    return new_time


@functions_framework.http
def adjust_scheduler_jobs(request):
    try:
        request_json = request.get_json()
        project_id = request_json['project_id']
        region = request_json['region']
        delta_range = 15  # Rango de 15 minutos para las variaciones

        min_morning = datetime.strptime("08:45", '%H:%M')
        max_morning = datetime.strptime("09:00", '%H:%M')

        min_afternoon_mon_thu = datetime.strptime("19:00", '%H:%M')
        max_afternoon_mon_thu = datetime.strptime("19:15", '%H:%M')

        min_afternoon_fri = datetime.strptime("16:45", '%H:%M')
        max_afternoon_fri = datetime.strptime("17:00", '%H:%M')

        min_13_30 = datetime.strptime("13:30", '%H:%M')
        max_13_30 = datetime.strptime("13:45", '%H:%M')

        min_14_15 = datetime.strptime("14:15", '%H:%M')
        max_14_15 = datetime.strptime("14:30", '%H:%M')

        # Ajusta el job de daily-task-13-30
        job_13_30_name = 'daily-task-13-30'
        #job_13_30_name_api = 'daily-task-13-30-api'

        schedule_time_13_30 = "13:30"
        job_13_30_new_time = update_scheduler_job(job_13_30_name, project_id, region, schedule_time_13_30, delta_range, min_13_30, max_13_30)
        #job_13_30_new_time_api = update_scheduler_job(job_13_30_name_api, project_id, region, schedule_time_13_30, delta_range, min_13_30, max_13_30)

        # Calcula el nuevo tiempo para daily-task-14-15 agregando 45 minutos
        job_14_15_name = 'daily-task-14-15'
        #job_14_15_name_api = 'daily-task-14-15-api'
        job_14_15_new_time = job_13_30_new_time + timedelta(minutes=45)
        #job_14_15_new_time_api = job_13_30_new_time_api + timedelta(minutes=45)

        # Asegúrate de que no exceda el rango permitido
        #if job_14_15_new_time < min_14_15 or job_14_15_new_time_api < min_14_15:
        if job_14_15_new_time < min_14_15:
            job_14_15_new_time = min_14_15
            #job_14_15_new_time_api = min_14_15
        elif job_14_15_new_time > max_14_15:
        #elif job_14_15_new_time > max_14_15 or job_14_15_new_time_api > max_14_15:
            job_14_15_new_time = max_14_15
            #job_14_15_new_time_api = max_14_15

        update_scheduler_job(job_14_15_name, project_id, region, "", 0, min_14_15, max_14_15, fixed_time=job_14_15_new_time)
        #update_scheduler_job(job_14_15_name_api, project_id, region, "", 0, min_14_15, max_14_15, fixed_time=job_14_15_new_time_api)

        # Ajusta los otros jobs
        other_jobs = [
            ('daily-task-morning', "09:02", min_morning, max_morning),
            ('daily-task-afternoon-mon-thu', "19:04", min_afternoon_mon_thu, max_afternoon_mon_thu),
            ('daily-task-friday', "16:47", min_afternoon_fri, max_afternoon_fri)
            #('daily-task-morning-api', "09:02", min_morning, max_morning),
            #('daily-task-afternoon-mon-thu-api', "19:04", min_afternoon_mon_thu, max_afternoon_mon_thu),
            #('daily-task-friday-api', "16:47", min_afternoon_fri, max_afternoon_fri)
        ]

        for job_name, schedule_time, min_time, max_time in other_jobs:
            update_scheduler_job(job_name, project_id, region, schedule_time, delta_range, min_time, max_time)

        return json.dumps({'status': 'success'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)}), 500
