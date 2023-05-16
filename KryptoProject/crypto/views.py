from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
import json
from .models import User as CryptoUser


@csrf_exempt
def login(request):
    if request.method == "POST":
        data = request.POST
        user = authenticate(username=data['name'], password=data['pass'])
        # user = "admin"
        response_data = {}
        if user is not None:
            auth_login(request, user)

            token, created = Token.objects.get_or_create(user=user)
            response_data['message'] = token.key

            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['message'] = None
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    return HttpResponse("{Don't know what to send}")

@login_required
def crypto(request):
    if request.method == "GET":
        # print(request.user._meta.fields)
        cryptoUser = CryptoUser.objects.get(user=request.user)
        response_data = {}
        response_data['message'] = "info"
        response_data['wallet'] = cryptoUser.user_data.wallet_dollars
        response_data['bit'] = cryptoUser.user_data.wallet_bit
        print(request.method)
        print(request.user)
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    return HttpResponse("{Don't know what to send}")
    # Create your views here.
