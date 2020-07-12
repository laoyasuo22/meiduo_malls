from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from .models import User
from django.contrib.auth import login
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    # 定义请求
    def post(self, request):
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        sms_code = request.POST.get('msg_code')
        allow = request.POST.get('allow')
        # 判断
        if not all([username, password, password2, mobile, sms_code, allow]):
            return http.HttpResponseForbidden('填写数据不为空')
        # 验证用户名
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名为5-20个字符')
        if User.objects.filter(username=username).count() > 0:
            return http.HttpResponseForbidden('用户名已存在')
        # 密码的验证
        if not re.match('^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('密码不符合规范请使用字符数字组合')
        if password != password2:
            return http.HttpResponseForbidden('两次密码输入不一致')
        # 手机号验证
        if not re.match('^1[3-9]\\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号码格式有误')
        if User.objects.filter(mobile=mobile).count() > 0:
            return http.HttpResponseForbidden('手机号码已经存在')
        # 电信密码读取
        redis_cli = get_redis_connection('sms_code')
        sms_code_redis = redis_cli.get(mobile)
        if sms_code_redis is None:
            return http.HttpResponseForbidden('验证码已过期')
        # 删除 验证码不可以使用第二次
        redis_cli.delete(mobile)
        # 判断是否正确
        if sms_code_redis.decode() != sms_code:
            return http.HttpResponseForbidden('验证码错误')
        # 处理

        # 创建用户对象
        user = User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )
        # 状态保持
        login(request, user)
        # 响应
        return redirect('/')


class UsernameView(View):
    def get(self, request, username):
        # 验证用户名是否存在
        count = User.objects.filter(username=username).count()
        # 响应
        return http.JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'ok'
        })


class MobileCountView(View):
    def get(self, request, mobile):
        # 验证用户名是否存在
        count = User.objects.filter(mobile=mobile).count()
        # 响应
        return http.JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'ok'
        })

    pass
