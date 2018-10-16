from io import BytesIO
import uuid

from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse

#判断是否为字典，如果是将抓拿华为JSON字符串
from django.http import JsonResponse

from django.forms.models import model_to_dict

from django.core.serializers import serialize
# Create your views here.
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST,require_http_methods
#引用django内置的分页模板
from django.core.paginator import Paginator

from . import utils
from . import models
from . import redis_utils
from .utils import require_login
from django.conf import settings

import logging

@require_login
def index(request):
    logger = logging.getLogger("django")
    logger.warning("首页开始运行了……")

    articles = redis_utils.get_all_articles(ischange=True)

    page_size = int(request.GET.get("page_size",settings.PAGE_SIZE))
    page_now = int(request.GET.get("page_now",1))
    paginator = Paginator(articles,page_size)
    page = paginator.page(page_now)

    return render(request,"demo/index.html",{"page":page,"page_size":page_size})


def login(request):
    if request.method == "GET":
        return render(request, "demo/login.html")
    elif request.method == "POST":
        username = request.POST["username"]
        passwords = request.POST["password"]
        password = utils.hmac_by_md5(passwords)
        # code = request.POST["code"]
        #
        # mycode = request.session["code"]
        # if code.upper() != mycode.upper():
        #     return render(request, "demo/login.html", {"msg": "验证码输入错误！"})
        # del mycode

        try:
            user = models.User.objects.get(username = username,password = password)
            #会话跟踪
            request.session["loginUser"] = user
            response = redirect(reverse("demo:index"))
            #使用cookie记录用户名称,cookie不能存储中文
            try:
                check_box = request.POST["check_box"]
                if check_box:
                    response.set_cookie("username",user.username,max_age=3600 * 24 * 14)
                    return response
            except:
                return response
        except:
            return render(request,"demo/login.html",{"msg":"登录失败，请重新登录！！"})

def register(request):
    if request.method == "GET":
        return render(request,"demo/register.html")
    elif request.method == "POST":
        try:
            username = request.POST["username"].strip()
            email = request.POST["email"].strip()
            password = request.POST["password"].strip()
            c_password = request.POST["c_password"].strip()

            if len(username) < 1:
                return render(request ,"demo/register.html", {"msg":"用户名称不能为空！！"})
            if len(password) < 6:
                return render(request, "demo/register.html", {"msg": "用户密码不能小于六位！！"})
            if password != c_password:
                return render(request, "demo/register.html", {"msg": "两次密码输入不一致！！"})
            if len(email) < 0:
                return render(request, "demo/register.html", {"msg": "邮箱不能为空！！"})
            try:
                user = models.User.objects.get(username = username)
                return render(request, "demo/register.html", {"msg": "账号已存在，请重新输入！！"})
            except:
                password = utils.hmac_by_md5(password)
                user = models.User(username = username,password = password,email = email)
                user.save()
                return render(request, "demo/login.html", {"msg": "账号注册成功,请登录！！"})
        except Exception as e:
            print(e)
            return render(request, "demo/register.html", {"msg": "账号不能为空"})

def show_index(request):
    return render(request, "demo/show_index.html")

@require_login
def update(request,u_id):
    user = models.User.objects.get(id=u_id)
    if request.method == "GET":
        return render(request,"demo/update.html", {"user":user})
    elif request.method == "POST":
        nickname = request.POST["nickname"]
        email = request.POST["email"]
        age = request.POST["age"]
        avatar = request.FILES.get("avatar",user.header)
        print(avatar)

        user.nickname = nickname
        user.email = email
        user.age = age
        user.header =  avatar
        request.session["loginUser"] = user
        user.save()
        return redirect(reverse("demo:index"))

#修改密码
def change_password(request, u_id):
    user = models.User.objects.get(pk=u_id)
    if request.method == "GET":
        return render(request,"demo/update.html", {"user":user})
    elif request.method == "POST":
        pwd = request.POST["pwd"]
        n_pwd = request.POST["n_pwd"]
        c_pwd = request.POST["c_pwd"]
        print(pwd,n_pwd,c_pwd)
        if len(n_pwd) < 6:
            # return render(request, "demo/update.html", {"user": user, "msg": "密码不能小于六位!"})
            return JsonResponse({"msg": "密码不能小于六位!","success":True})

        if utils.hmac_by_md5(pwd) == user.password:
            if n_pwd == c_pwd:
                user.password = utils.hmac_by_md5(n_pwd)
                user.save()
                # return  render(request,"demo/login.html")
                return JsonResponse({"msg": "密码修改成功", "success": False})
            else:
                # return render(request,"demo/update.html", {"user":user,"msg":"两次密码输入不一致!"})
                # return redirect(reverse("demo:change_password", kwargs={"user":user,"msg":"两次密码输入不一致!"}))
                return JsonResponse({"msg": "两次密码输入不一致!", "success": True})
        else:
            # return render(request, "demo/update.html", {"user": user, "msg": "原密码输入错误！"})
            # return redirect(reverse("demo:change_password", kwargs={"user": user, "msg": "密码输入错误！"}))
            return JsonResponse({"msg": "原密码输入错误！", "success": True})


def delete_user(request,u_id):
    user = models.User.objects.get(pk=u_id)
    user.delete()
    return redirect("/demo/show_index/")


def logout(request):
    try:
        del request.session["loginUser"]

    finally:
        return redirect(reverse("demo:show_index"))


@require_login
def add_article(request):
    if request.method == "GET":
        return render(request, "demo/add_article.html")
    elif request.method == "POST":
        title = request.POST["title"]
        content1 = request.POST["content"]
        author = request.session["loginUser"]

        content = utils.clear_html_re(content1)
        article = models.Article(title=title, content=content,author=author)
        article.save()
        #把数据添加到缓存中
        redis_utils.get_self_article(author=author, ischange=True)
        redis_utils.get_all_articles()

        return JsonResponse({"msg": "文章添加成功", "success": True})
        # return redirect(reverse("demo:show_article", kwargs={"a_id": article.id}))

@require_login
def show_article(request,a_id):

    at = models.Article.objects.get(pk=a_id)
    return render(request,"demo/show_article.html",{"article":at})


@require_login
def self_article(request):
    articles = redis_utils.get_self_article(author=request.session["loginUser"])
    return render(request,"demo/self_article.html",{"articles":articles})


@require_login
def update_article(request,a_id):
    at = models.Article.objects.get(pk=a_id)
    if request.method == "GET":
        return render(request, "demo/update_article.html", {"at": at})
    else:
        title = request.POST["title"]
        content = request.POST["content"]
        at.content = content
        at.title = title
        at.save()
        return redirect(reverse("demo:self_article"))

def delete_article(request, a_id):
    at = models.Article.objects.get(pk=a_id)
    author = request.session["loginUser"]
    at.delete()
    redis_utils.get_self_article(author=author, ischange=True)
    return redirect(reverse("demo:self_article"))


def code(request):
    img, code = utils.create_code()
    #将数据保存到session
    request.session["code"] = code

    file = BytesIO()
    img.save(file,'PNG')

    return HttpResponse(file.getvalue(), "image/png")


# @require_http_methods("GET","POST")
# @require_POST
# # @csrf_exempt
# def ajax_hello(request):
#     id = request.POST["id"]
#     name = request.POST["name"]
#     print(id,name)
#     #model_to_dict(at)先将对象转化为字典对象，然后转化为JSON对象
#     #at = models.Article.objects.get(pk=id)
#     # return JsonResponse(model_to_dict(at))
#     ats = models.Article.objects.all()
#     return HttpResponse(serialize("json",ats))

def check_username(request,username):
    qs = models.User.objects.filter(username=username)
    if len(qs):
        return JsonResponse({"msg":"该用户名已存在，请从新输入！！","success":False})
    else:
        return JsonResponse({"msg":"恭喜您，用户名可用！！","success":True})