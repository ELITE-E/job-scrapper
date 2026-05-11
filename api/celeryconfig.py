# Celery configuration.

# Serialization settings (JSON only).
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# Timezone settings.
timezone = "UTC"
enable_utc = True

# Result expiration (seconds).
result_expires = 3600  # 1 hour

# Task tracking.
task_track_started = True

# Retry broker connection on worker start.
broker_connection_retry_on_startup = True
#prevents memory leaks in long-running workers.
worker_max_tasks_per_child = 50

# Prevent long-running tasks from being re-queued prematurely.
#broker_transport_options = {"visibility_timeout": 43200}  # 12 hours

from celery.schedules import crontab

beat_schedule = {
	#"scrape-jobs-every-6-hours"
    "scrape-jobs-every-2-mins": {
		"task": "app.tasks.scrape_jobs_task",
		#"schedule": crontab(minute=0, hour="*/6"),
        'schedule': crontab(minute='*/8'),
	},
}
