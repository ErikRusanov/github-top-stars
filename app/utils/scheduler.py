from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.repos import repos_service


def configure_scheduler():
    scheduler = AsyncIOScheduler()
    # In top repositories, the number of stars, views, forks, etc. can change quite quickly, so a frequency of 5
    # minutes, in my opinion, is optimal. Subject to authorized requests with a limit of 5000 requests per hour,
    # this will not greatly limit the possibilities for parsing activities

    for hour in range(0, 24):
        for minute in range(0, 60, 5):
            trigger = CronTrigger(hour=hour, minute=minute)
            scheduler.add_job(
                repos_service.update_top_repos,
                trigger=trigger,
            )

    return scheduler
