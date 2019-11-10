from django.http.response import HttpResponse
import json
from datetime import date, datetime, timedelta, timezone
from time import localtime, mktime, time

def decode_uni(str):
    str.decode('unicode-escape')

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def add_header(output,state=200):
    response = HttpResponse(json.dumps(output, default=json_serial), content_type="application/json",status=state)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, PUT, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def return_header(state=200):
    response = HttpResponse(status=state)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, PUT, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def getBody(request):
    body_unicode = request.body.decode('utf-8')
    return json.loads(body_unicode)

def strToDateTime(str,format):
    tm = datetime.strptime(str,format)
    return tm

def getNow():
    JST = timezone(timedelta(hours=+9), 'JST')
    return datetime.now(JST)

def setUpDt(dt):
    dt['update_at'] = datetime.now().strftime('%Y-%m-%d')
    return dt
