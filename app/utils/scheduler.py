from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.repos import repos_service


def configure_scheduler():
    """
    Configures and returns an AsyncIOScheduler with a cron job to update top repositories.

    This scheduler is designed to run the update_top_repos function at regular intervals, allowing
    for timely updates of top repositories based on star, view, fork, etc. counts.

    The chosen frequency is set to every 1 minutes, providing a balance between quick updates and
    complying with authorized requests with a limit of 5000 requests per hour.

    :return: Configured AsyncIOScheduler instance.
    """
    scheduler = AsyncIOScheduler()

    # Setting up cron jobs for each 1-minute interval within a 24-hour period
    for hour in range(0, 24):
        for minute in range(0, 60):
            trigger = CronTrigger(hour=hour, minute=minute)
            scheduler.add_job(
                repos_service.update_top_repos,
                trigger=trigger,
            )

    return scheduler
