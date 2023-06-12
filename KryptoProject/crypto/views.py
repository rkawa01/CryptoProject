from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.middleware import csrf
from django.contrib.auth.decorators import login_required
import json
from .models import User as CryptoUser


@csrf_exempt
def login(request):
    if request.method == "POST":
        data = request.POST
        user = authenticate(username=data['name'], password=data['pass'])

        response_data = {}
        if user is not None:
            auth_login(request, user)
            token = csrf.get_token(request)

            # token, created = Token.objects.get_or_create(user=user) // token.key

            response_data['message'] = token

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
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif request.method == "POST":
        data = request.POST
        cryptoUser = CryptoUser.objects.get(user=request.user)
        # set with converting to double from string
        cryptoUser.user_data.wallet_dollars = float(data['wallet'])
        cryptoUser.user_data.wallet_bit = float(data['bit'])
        cryptoUser.user_data.save()
        response_data = {}
        response_data['message'] = "info"
        return HttpResponse(json.dumps(response_data), content_type="application/json")



    return HttpResponse("{Don't know what to send}")
    # Create your views here.


# Example of authentication with rest_framework.authtoken
# token_key = request.POST.get('token')
# # Check if the token is valid
# try:
#     token = Token.objects.get(key=token_key)
#
# except Token.DoesNotExist:
#     return HttpResponse("Invalid token", status=401)
#
# user = token.user
#
# if user is not None:
#     auth_login(request, user)
#     response_data = {}
#     response_data['message'] = "info"
#     return HttpResponse(json.dumps(response_data), content_type="application/json")
# else:
#     return HttpResponse("Authentication failed", status=401)