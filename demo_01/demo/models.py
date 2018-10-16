from datetime import datetime

from django.db import models

from DjangoUeditor.models import UEditorField
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名称")
    password = models.CharField(max_length=50, verbose_name="用户密码")
    age = models.IntegerField(default=18, verbose_name="用户年龄")
    nickname = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, verbose_name="用户邮箱")
    gender = models.BooleanField(default=0)  # 默认是0 表示男生，1表示女生
    header = models.ImageField(upload_to="static/demo/image/headers/",default="static/demo/image/headers/9.jpg",verbose_name="用户头像")

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255,verbose_name="文章标题")
    # content = models.TextField(verbose_name="文章内容")
    content = UEditorField()
    publishtime = models.DateTimeField(auto_now_add=True)
    modifyTime = models.DateTimeField(auto_now=True)

    #外键
    author = models.ForeignKey(User,on_delete=models.CASCADE)