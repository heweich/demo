from django.contrib import admin

from .import models
# Register your models here.
class UserAdmin(admin.ModelAdmin):
 # 列表页面要显示属性
     list_display = ["username", "nickname", "age"]
     # 过滤的属性
     list_filter = ["age"]
     # 分页的每页数量
     list_per_page = 2
     # 增加和修改的属性
     # fields = ["name", "nickname"]
     # 注意，fields 和 fieldsets 不能同时出现
     # fieldsets = [
     # ("base", {"fields": ["age", "birthday"]}),

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Article)