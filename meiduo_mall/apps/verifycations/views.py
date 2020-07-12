import random

from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constans
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.libs.yuntongxun.sms import CCP


# Create your views here.
class ImageCode(View):
    def get(self, request, uuid):
        # 接受
        # 验证
        # 处理
        # 1，生成
        text, code, image = captcha.generate_captcha()
        # 2，保存 键值对redis
        redis_cli = get_redis_connection('image_code')
        redis_cli.setex(uuid, constans.IMAGE_CODE_EXPIRES, code)

        return http.HttpResponse(image, content_type='image/png')

    pass


class SmsCode(View):
    def get(self, request, mobile):
        # 接受uuid
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        # 验证 是否存在六十秒
        redis_cli = get_redis_connection('sms_code')
        if redis_cli.get(mobile + '_flag') is not None:
            return http.JsonResponse({
                'code': RETCODE.SMSCODERR,
                'errmsg': '发送短信太频繁。。'
            })
        if not all([uuid, image_code]):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '参数不完整'
            })
        # 图形验证码是否正确
        redis_cli = get_redis_connection('image_code')
        image_code_redis = redis_cli.get(uuid)
        if image_code_redis is None:
            return http.JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效，点击更换一个'
            })
        # 删除图形验证码 表示不能使用第二次
        redis_cli.delete(uuid)
        if image_code_redis.decode().lower() != image_code.lower():
            return http.JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码错误'
            })
        # 生成随机数
        sms_code = "%06d" % random.randint(0, 999999)
        redis_cli.setex(mobile, constans.SMS_CODE_EXPIRES, sms_code)
        # 写发标志防止 重复刷新
        redis_cli.setex(mobile + '_flag', constans.SMS_CODE_FLAG, 1)
        # 发短信
        # ccp.send_template_sms(mobile, [sms_code,constans.SMS_CODE_EXPIRES/60],1)
        print(sms_code)
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok'
        })

    pass
