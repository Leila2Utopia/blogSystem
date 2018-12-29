from django import template
from blog.models import *
from django.db.models import Count

register=template.Library()

@register.inclusion_tag("menu.html")
def get_query_data(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count("article")).values_list("title","c")
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article")).values_list("title","c")
    data_list = Article.objects.filter(user=user).extra(select={"time":"strftime('%%Y-%%m',create_time)"}).\
        values("time").annotate(c=Count("title")).values_list("time","c")
    return {"username":username,"cate_list":cate_list,"tag_list":tag_list,"date_list":data_list,"blog":blog}


