from django.shortcuts import render,HttpResponse,redirect
import json
from django.contrib import auth
from blog.forms import *
from django.contrib.auth.models import User
from blog.models import *
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from bs4 import BeautifulSoup
import os
from taskBlog_ll import settings

# Create your views here.
def login(request):

    if request.is_ajax():
        res = {"user":None,"msg":None}
        user = request.POST.get("name")
        pwd = request.POST.get("pwd")
        valid = request.POST.get('valid')
        random_str =request.session.get("random_str")
        if valid.upper() == random_str.upper():
            user = auth.authenticate(username=user,password=pwd)
            if user:
                res["user"]=user.username
                auth.login(request,user)
            else:
                res["msg"]="用户名或密码错误"
        else:
            res["msg"]="验证码错误"

        return HttpResponse(json.dumps(res))

    return render(request,"login.html")

def login_success(request):
    obj=redirect('/index/')
    return obj

def index(request):
    article_list = Article.objects.all()
    try:
        paginator = Paginator(article_list,6)
        c_page = request.GET.get("page",1)
        page = paginator.page(c_page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return render(request,'index.html',locals())

def valid_img(request):
    import random
    from PIL import Image
    from PIL import ImageDraw, ImageFont
    from io import BytesIO
    # 随机颜色
    def get_random_color():
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    # 生成随机图片
    image = Image.new('RGB',(250,36),color=get_random_color())
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("blog/static/font/kumo.ttf",size=32)
    random_str=""
    for i in range(5):
        random_num = str(random.randint(0,9))
        random_low_alpha = chr(random.randint(97,122))
        random_up_alpha = chr(random.randint(65,90))
        random_char = random.choice([random_num,random_low_alpha,random_up_alpha])
        draw.text((20+i*40,0),random_char,get_random_color(),font=font)
        random_str += random_char
    print(random_str)
    request.session["random_str"]=random_str
    #噪点噪线
    width = 250
    height = 36
    for i in range(5):
        x1 = random.randint(0,width)
        x2 = random.randint(0,width)
        y1 = random.randint(0,height)
        y2 = random.randint(0,height)
        draw.line((x1,y1,x2,y2),fill=get_random_color())

    for i in range(20):
        draw.point([random.randint(0,width),random.randint(0,height)],fill=get_random_color())
        x =random.randint(0,width)
        y = random.randint(0,height)
        draw.arc((x,y,x+4,y+4),0,90,fill=get_random_color())

    #从缓存中读取图片
    f = BytesIO()
    image.save(f,'png')
    data = f.getvalue()
    return HttpResponse(data)

def reg(request):
    if request.is_ajax():
        res={"user":None,"msg":None}
        form = UserForm(request.POST)
        print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        repeat_pwd = request.POST.get("repeat_pwd")
        email = request.POST.get("email")
        file_obj = request.FILES.get('avatar')

        if form.is_valid():
            user = UserInfo.objects.create_user(username=username,password=password,email=email,avator=file_obj)
            user.save()
            res['user']=user.username
            return HttpResponse(json.dumps(res))
        else:
            res['msg']=form.errors
            print(form.errors)
            return HttpResponse(json.dumps(res))
    return render(request,'reg.html',locals())

def logout(request):
    auth.logout(request)
    return redirect('/index/')

def homesites(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    if kwargs:
        condition=kwargs.get("condition")
        params=kwargs.get("params")
        if condition == 'cate':
            article_list = Article.objects.filter(user=user).filter(category__title=params)
        elif condition == 'tag':
            article_list = Article.objects.filter(user=user).filter(tags__title=params)
        else:
            year,month=params.split("-")
            article_list = Article.objects.filter(user=user).filter(create_time__year=year,create_time__month=month)
    else:
        article_list = Article.objects.filter(user=user)
    try:
        paginator = Paginator(article_list,6)
        c_page = request.GET.get("page",1)
        page = paginator.page(c_page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # print(article_list)
    # print("count", paginator.count)
    # print("num_pages", paginator.num_pages)
    # print("page_range", paginator.page_range)

    return render(request,"homesite.html",locals())


def article_detail(request,username,article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)

    return render(request,"article_detail.html",locals())

def digg(request):
    res={"state":True}
    user_pk=request.user.pk
    article_id=request.POST.get("article_id")
    is_up=request.POST.get("is_up")
    is_up=json.loads(is_up)
    try:
        with transaction.atomic():
            ArticleUpdown.objects.create(user_id=user_pk,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        res["state"]=False
        res["first_action"]=ArticleUpdown.objects.filter(user_id=user_pk,article_id=article_id).first().is_up


    return JsonResponse(res)

def comment(request):
    user_pk=request.user.nid
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    pid=request.POST.get("pid")

    response={}
    with transaction.atomic():
        # 提交根评论
        if not pid:
            comment_obj=Comment.objects.create(user_id=user_pk,article_id=article_id,content=content)
        # 提交子评论
        else:
            comment_obj = Comment.objects.create(user_id=user_pk, article_id=article_id, content=content,parent_comment_id=pid)

        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response["ctime"]=comment_obj.create_time.strftime("%Y-%m-%d %H:%M")
    response["content"]=comment_obj.content

    return JsonResponse(response)

def comment_tree(request,article_id):
    # 评论树
    comment_list=list(Comment.objects.filter(article_id=article_id).values("content","pk","parent_comment_id"))
    print(comment_list)
    return JsonResponse(comment_list,safe=False)

def add_article(request):
    if request.method=='POST':
        title=request.POST.get("title")
        article_content=request.POST.get("article_content")

        bs=BeautifulSoup(article_content,"html.parser")

        for tag in bs.find_all():
            if tag.name=='script':
                tag.decompose()

        article_content=bs.prettify()
        desc=bs.text[0:150]
        obj=Article.objects.create(user=request.user,title=title,desc=desc)
        ArticleDetail.objects.create(article=obj,content=article_content)

        return HttpResponse('OK')

    return render(request,"add_article.html")

def upload(request):
    obj=request.FILES.get("upload_img")
    path=os.path.join(settings.MEDIA_ROOT,"articles",obj.name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)

    res={
        "error":0,
        "url":"/media/articles/"+obj.name
    }

    return HttpResponse(json.dumps(res))

