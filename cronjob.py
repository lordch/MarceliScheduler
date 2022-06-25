from apscheduler.schedulers.blocking import BlockingScheduler

from main import synchronize_dbs

scheduler = BlockingScheduler(timezone="Europe/Warsaw")
scheduler.add_job(synchronize_dbs, "date", run_date="2022-06-25 18:40:05")

scheduler.start()
