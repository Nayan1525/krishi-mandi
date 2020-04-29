import json
from django.http.response import  HttpResponse
def parameter_missing_error(parameter):
    return HttpResponse(json.dumps({"message":"{parameter} is missing".format(parameter=parameter)}),status=422)

def create_success_response(message,data):
    data = json.loads(data)
    return HttpResponse(json.dumps({"message":message,"data":data}),status=201)

def server_error_response():
    return HttpResponse(json.dumps({"message":"internal server error"}),status=500)

