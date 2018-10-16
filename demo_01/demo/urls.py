from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index/$',views.index,name='index'),
    url(r'^login/$',views.login,name='login'),
    url(r'^register/$',views.register,name='register'),
    url(r'^show_index/$',views.show_index,name='show_index'),
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^(?P<u_id>\d+)/update/$', views.update, name="update"),
    url(r'^(?P<u_id>\d+)/change_password/$', views.change_password, name="change_password"),
    url(r'^(?P<u_id>\d+)/delete_user/$', views.delete_user, name="delete_user"),

    #文章的增删改查
    url(r"^add_article/$",views.add_article,name='add_article'),
    url(r"^(?P<a_id>\d+)/show_article/$",views.show_article,name='show_article'),
    url(r"self_article/$",views.self_article,name='self_article'),
    url(r"^(?P<a_id>\d+)/update_article/$",views.update_article,name='update_article'),
    url(r"^(?P<a_id>\d+)/delete_article/$",views.delete_article,name='delete_article'),

    #验证码
    url(r'^code/$',views.code,name='code'),

    url(r'^(?P<username>\w+)/check_username/$',views.check_username, name='check_username'),
]
