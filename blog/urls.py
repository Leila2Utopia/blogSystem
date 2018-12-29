
from django.conf.urls import url
from blog import views



urlpatterns = [
    url(r"digg/",views.digg),
    url(r'comment/',views.comment),
    url(r'add_article',views.add_article),
    url(r'comment_tree/(\d+)',views.comment_tree),
    url(r'^(?P<username>\w+)/$',views.homesites),
    url(r'^(?P<username>\w+)/(?P<condition>tag|cate|achrive)/(?P<params>.*)',views.homesites),
    url(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)',views.article_detail),
]
