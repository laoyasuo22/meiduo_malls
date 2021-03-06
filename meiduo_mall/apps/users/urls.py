from django.conf.urls import url
from . import views

urlpatterns = [
    url('^register/$', views.RegisterView.as_view()),
    url('^login/$', views.LoginView.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',
        views.MobileCountView.as_view()),
]
