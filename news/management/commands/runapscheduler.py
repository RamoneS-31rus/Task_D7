import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from django_apscheduler.models import DjangoJobExecution
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler import util

from news.models import Post, Category, Subscriber


logger = logging.getLogger(__name__)

def my_job():
    week = datetime.now() - timedelta(days=7)    
    subscribers = Subscriber.objects.all()
    
    for sub in subscribers:        
        posts = [Post.objects.filter(category=cat, date_create__gt=week) for cat in sub.category.all()]
        posts = set([item for sublist in posts for item in sublist])

        email = sub.user.email
    
        subject = f'Публикации за неделю в Ваших подписках'

        if posts:       
            text_content = str([f'{post.title}: http://127.0.0.1:8000{post.get_absolute_url()}\n' for post in posts])
            html_content = str([f'<a href="http://127.0.0.1:8000{post.get_absolute_url()}"><b>{post.title}</b></a><br>' for post in posts])        
            
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()      
             

def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="fri", hour="18", minute="00"),
            # trigger=CronTrigger(second="*/10"),            
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),            
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
