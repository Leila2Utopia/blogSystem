from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(UserInfo)
admin.site.register(Blog)
admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(ArticleDetail)
admin.site.register(Article2Tag)
admin.site.register(ArticleUpdown)
admin.site.register(Comment)