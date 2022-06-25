from apscheduler.schedulers.blocking import BlockingScheduler

from main import synchronize_dbs

scheduler = BlockingScheduler(timezone="Europe/Warsaw")
scheduler.add_job(synchronize_dbs, "cron", hour=3)

scheduler.start()
