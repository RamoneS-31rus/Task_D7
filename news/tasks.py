from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from celery import shared_task

from .models import Post, Category, Subscriber


@shared_task()
def notify_post(post_id):
    post = Post.objects.get(id=post_id)
    categories = post.category.all().values_list('id', flat=True)
    emails = [(User.objects.filter(subscriber__category=i).values_list("email", flat=True)) 
               for i in categories]
    emails = set([item for sublist in emails for item in sublist])
    
    subject = f'Доступна новая публикация'
    title = post.title
    text = post.preview()
    url = f'http://127.0.0.1:8000{post.get_absolute_url()}'
    
    text_content = (
        f'{title}\n'
        f'{text}\n'
        f'Ссылка на публикацию: {url}'
    )    

    html_content = render_to_string('email/new_post.html', {
                                                            'title': title, 
                                                            'text': text, 
                                                            'url': url,
                                                            }
                                    )
    
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])  # при None берётся почта по умолчанию из settings
        msg.attach_alternative(html_content, "text/html")
        msg.send()
 

@shared_task()
def send_newsletter():
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
    