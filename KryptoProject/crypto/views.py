from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
@csrf_exempt
def index(request):
    print(request.user)
    if request.method == "POST":
        data = request.POST
        q = User.objects.filter(login_field=data['name'], password_field=data['pass'])
        # print(q.count())
        response_data = {}
        if(q.count() == 1):
            response_data['message'] = 'OK'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['message'] = 'NOTOK'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    return HttpResponse("{Don't know what to send}")

# Create your views here.
