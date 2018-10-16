import random,string
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from django.shortcuts import render
from django.conf import settings

import hashlib
import hmac
import logging
import re

from django.conf import settings
from demo_01 import settings

# 获取一个随机字符串，4位的
def getRandomChar(count=4):
    # 生成随机字符串
    # string模块包含各种字符串，以下为小写字母加数字
    ran = string.ascii_lowercase + string.ascii_uppercase + string.digits
    char = ''
    for i in range(count):
        char += random.choice(ran)
    return char


# 返回一个随机的RGB颜色
def getRandomColor():
    return (random.randint(50,150),random.randint(50,150),random.randint(50,150))


def create_code():
    # 创建图片，模式，大小，背景色
    img = Image.new('RGB', (120,30), (210,200,255))
    #创建画布
    draw = ImageDraw.Draw(img)
    # 设置字体
    font = ImageFont.truetype('arial.ttf', 25)

    code = getRandomChar()
    # 将生成的字符画在画布上
    for t in range(4):
        draw.text((30*t+5,0),code[t],getRandomColor(),font)

    # 生成干扰点
    for _ in range(random.randint(0,200)):
        # 位置，颜色
        draw.point((random.randint(0, 120),random.randint(0, 30)),fill=getRandomColor())

    # 使用模糊滤镜使图片模糊
    # img = img.filter(ImageFilter.BLUR)
    # 保存
    # img.save(''.join(code)+'.jpg','jpeg')
    return img,code

#简单加密
def hash_by_md5(pwd):
    md5 = hashlib.md5(pwd.encode('utf-8'))
    md5.update(settings.MD5_SALT.encode('utf-8'))
    return md5.hexdigest()

#复杂加密
def hmac_by_md5(pwd):
    return hmac.new(pwd.encode('utf-8'), settings.MD5_SALT.encode('utf-8'), "MD5").hexdigest()


#装饰器，判断用户是否登录
def require_login(fn):

    def inner(request,*args, **kwargs):
        if request.session.has_key("loginUser"):
            logging.warning("该用户已经登录，视图函数正常访问")
            return fn(request, *args, **kwargs)
        else:
            logging.warning("请先登录！！")
            return render(request,"demo/login.html", {"msg": "当前操作必须登录，请先登录系统"})
    return inner


#使用正则，剔除发表文章中的标签
def clear_html_re(content):
    s_content = re.sub(r"<(.+?)>","",content)
    logging.warning(s_content)
    return s_content


if __name__ == '__main__':
    pass
