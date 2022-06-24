from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
from test_job import test_job

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(test_job, "interval", seconds=30)

scheduler.start()
