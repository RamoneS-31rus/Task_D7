from django.contrib import admin
from .models import (
    Author,
    Category,
    Subscriber,
    SubscriberCategory,
    Post,
    PostCategory,
    Comment,
)


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Subscriber)
admin.site.register(SubscriberCategory)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)
