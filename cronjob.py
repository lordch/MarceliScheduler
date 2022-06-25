from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
# from test_job import test_job
from main import synchronize_dbs

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler(timezone="Europe/Warsaw")
# scheduler.add_job(test_job, "interval", seconds=30)
scheduler.add_job(synchronize_dbs, 'date', run_date='2022-06-25 18:40:05')

scheduler.start()
