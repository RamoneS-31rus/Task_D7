# from django.contrib.auth.models import User
# from django.db.models.signals import m2m_changed
# from django.dispatch import receiver
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string

# from .models import Post, Category


# @receiver(m2m_changed, sender=Post.category.through)
# def notify_post(instance, action, **kwargs):    
#     if action == 'post_add':    
#         categories = instance.category.all().values_list('id', flat=True)

#         emails = [(User.objects.filter(subscriber__category=i).values_list("email", flat=True)) 
#                 for i in categories]
#         emails = set([item for sublist in emails for item in sublist])
        
#         subject = f'Доступна новая публикация'
        
#         text_content = (
#             f'{instance.title}\n'
#             f'{instance.preview()}\n'
#             f'Ссылка на публикацию: http://127.0.0.1:8000{instance.get_absolute_url()}'
#         )
#         print(type(text_content))
#         html_content = (
#             f'<b>{instance.title}</b><br>'
#             f'{instance.preview()}<br>'
#             f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
#             f'Ссылка на публикацию</a>'
#         )
#         for email in emails:
#             msg = EmailMultiAlternatives(subject, text_content, None, [email])
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()
