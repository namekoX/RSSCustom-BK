from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import feedparser
from .models import Entry, LoginUser
from .forms import EntryForm, LoginUserForm
from common import util
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
import time
from django.forms.models import model_to_dict
from django.db.models import Q

def get_title(request):
    if request.method != 'GET':
        return HttpResponse(status=412)

    if "url" in request.GET:
        url = request.GET.get("url")
    else:
        return HttpResponse(status=412)

    d = feedparser.parse(url)
    ret = {"title":d.feed.title , "version":d.version}
    return util.add_header(ret)

@csrf_exempt
def get_entry_list(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'GET':
        return HttpResponse(status=412)

    if "page" in request.GET:
        page = int(request.GET.get("page"))
    else:
        return HttpResponse(status=412)

    if "perpage" in request.GET:
        perpage = int(request.GET.get("perpage"))
    else:
        return HttpResponse(status=412)

    if "site_name" in request.GET:
        site = request.GET.get("site_name")
        cond = Q(site_name__contains=site)
    else:
        cond = Q()

    if "user_id" in request.GET:
        userid = request.GET.get("user_id")
        cond2 = Q(user_id__contains=userid)
    else:
        cond2 = Q(user_id=None)

    data = Entry.objects.filter(cond , cond2).order_by('no').reverse().values('no','url','site_name','version', 'user_id')[(page - 1) * perpage : page * perpage]
    count = Entry.objects.filter(cond , cond2).count()
    list_result = [entry for entry in data]
    res = {"tableData" : list_result, "pagerTotalCount" : count}
    return util.add_header(res)

@csrf_exempt
def get_entry(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'GET':
        return HttpResponse(status=412)
    if "entryNo" in request.GET:
        entryNo = request.GET.get("entryNo")
    else:
        return HttpResponse(status=412)
    if "user_id" in request.GET:
        user = request.GET.get("user_id")
    else:
        user = None

    obj = Entry.objects.get(no=entryNo, user_id=user)
    return util.add_header(model_to_dict(obj))

@csrf_exempt
def create_entry(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)
    obj = Entry()
    info = EntryForm(util.getBody(request), instance=obj)
    info.save()
    ret = {"entryNo":obj.no}
    return util.add_header(ret)

def get_rss(request, entryno):
    if request.method != 'GET':
        return HttpResponse(status=412)
    if "ver" in request.GET:
        ver = request.GET.get("ver")
    else:
        return HttpResponse(status=412)

    obj = Entry.objects.get(no=entryno)
    url = obj.url

    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",}
    req = urllib.request.Request(url=url, headers=headers)
    with urllib.request.urlopen(req) as response:
        xml_string = response.read()

    try:
        ET.register_namespace('', 'http://purl.org/rss/1.0/')
        ET.register_namespace('', 'http://www.w3.org/2005/Atom')
        root = ET.fromstring(xml_string)
    except:
        return HttpResponse("RSSの解析に失敗しました。このサイトでは対応できない形式のようです。")

    if ver == "rss2":
        # RSS2
        channel = root.findall("channel")[0]
    else:
        # RSS1、ATOM
        channel = root

    if channel.find("item") is not None:
        # RSS2
        items = channel.findall("item")
    elif channel.find("{http://purl.org/rss/1.0/}item") is not None:
        # RSS1
        items = channel.findall("{http://purl.org/rss/1.0/}item")
    elif channel.find("{http://www.w3.org/2005/Atom}entry") is not None:
        # ATOM
        items = channel.findall("{http://www.w3.org/2005/Atom}entry")
    else:
        return HttpResponse("RSSの解析に失敗しました。このサイトでは対応できない形式のようです。")

    i = 0
    now = util.getNow()
    for item in items:
        deleteflg = False
        # カテゴリ
        if obj.inclede_category is not None:
            deleteflg = True
            if item.find("category") is not None:
                # RSS2
                categorys = item.findall("category")
                for category in categorys:
                    if category.text is not None:
                        if (obj.inclede_category in category.text):
                            deleteflg = False
            elif item.find("{http://purl.org/dc/elements/1.1/}subject") is not None:
                #RSS1
                categorys = item.findall("{http://purl.org/dc/elements/1.1/}subject")
                for category in categorys:
                    if category.text is not None:
                        if (obj.inclede_category in category.text):
                            deleteflg = False
            elif item.find("{http://www.w3.org/2005/Atom}category") is not None:
                #ATOM
                categorys = item.findall("{http://www.w3.org/2005/Atom}category")
                for category in categorys:
                    if (obj.inclede_category in category.get("term", "")):
                        deleteflg = False
            else:
                deleteflg = False
        # 件名
        if obj.inclede_subject is not None:
            if item.find("title") is not None:
                # RSS2
                if (obj.inclede_subject not in item.findtext("title")):
                    deleteflg = True
            elif item.find("{http://purl.org/rss/1.0/}title") is not None:
                # RSS1
                if (obj.inclede_subject not in item.findtext("{http://purl.org/rss/1.0/}title")):
                    deleteflg = True
            elif item.find("{http://www.w3.org/2005/Atom}title") is not None:
                # ATOM
                if (obj.inclede_subject not in item.findtext("{http://www.w3.org/2005/Atom}title")):
                    deleteflg = True
        # 投稿者
        if obj.inclede_creater is not None:
            if item.find("author") is not None:
                # RSS2
                if item.findtext("author") is not None:
                    if (obj.inclede_creater not in item.findtext("author")):
                        deleteflg = True
            elif item.find("{http://purl.org/dc/elements/1.1/}creator") is not None:
                # RSS1
                if item.findtext("{http://purl.org/dc/elements/1.1/}creator") is not None:
                    if (obj.inclede_creater not in item.findtext("{http://purl.org/dc/elements/1.1/}creator")):
                        deleteflg = True
            elif item.find("{http://www.w3.org/2005/Atom}author") is not None:
                # ATOM
                author = item.find("{http://www.w3.org/2005/Atom}author")
                if author.findtext("{http://www.w3.org/2005/Atom}name") is not None:
                    if (obj.inclede_creater not in author.findtext("{http://www.w3.org/2005/Atom}name")):
                        deleteflg = True
        # 投稿日時
        if obj.limit_day is not None:
            basetime = now - datetime.timedelta(days=obj.limit_day)
            if item.findtext("pubDate") is not None:
                # RSS2
                dt = util.strToDateTime(item.findtext("pubDate"),"%a, %d %b %Y %H:%M:%S %z")
                if basetime > dt:
                    deleteflg = True
            if item.findtext("{http://purl.org/dc/elements/1.1/}date") is not None:
                # RSS1
                dt = util.strToDateTime(item.findtext("{http://purl.org/dc/elements/1.1/}date"),"%Y-%m-%dT%H:%M:%S%z")
                if basetime > dt:
                    deleteflg = True
            if item.findtext("{http://www.w3.org/2005/Atom}updated") is not None:
                # ATOM
                dt = util.strToDateTime(item.findtext("{http://www.w3.org/2005/Atom}updated"),"%Y-%m-%dT%H:%M:%S%z")
                if basetime > dt:
                    deleteflg = True
        # 最大件数
        if obj.max_count is not None:
            if i >=  obj.max_count:
                deleteflg = True

        if deleteflg:
            channel.remove(item)
        else:
            i += 1


    ret = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n" + str(ET.tostring(root),"utf-8")
    return HttpResponse(ret, content_type="text/xml", status=200)

@csrf_exempt
def update_entry(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)
    body = util.getBody(request)
    body = util.setUpDt(body)

    obj = Entry.objects.get(no=body.get("entryNo"), user_id=body.get("user_id"))
    obj = EntryForm(body, instance=obj)
    obj.save()
    return util.return_header(200)

@csrf_exempt
def delete_entry(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)
    body = util.getBody(request)

    obj = Entry.objects.get(no=body.get("entryNo"), user_id=body.get("user_id"))
    obj.delete()
    return util.return_header(200)

@csrf_exempt
def create_user(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)

    body = util.getBody(request)

    if LoginUser.objects.filter(user_id=body.get("user_id"), site_id ='1').exists():
        ret = {"Msg":"指定されたユーザIDはすでに登録されています。別のユーザIDを入力してください。","OK":False}
        return util.add_header(ret)

    obj = LoginUser()
    info = LoginUserForm(body, instance=obj)
    info.save()
    ret = {"Msg":"登録しました","OK":True}
    return util.add_header(ret)

@csrf_exempt
def update_user(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)

    body = util.getBody(request)

    obj = LoginUser(user_id=body.get("user_id"), site_id ='1')
    obj.password = body.get("password")
    obj.update_at = datetime.datetime.now().strftime('%Y-%m-%d')
    obj.save()
    ret = {"Msg":"更新しました","OK":True}
    return util.add_header(ret)

@csrf_exempt
def login(request):
    if request.method == 'OPTIONS':
        return util.return_header(200)
    if request.method != 'POST':
        return HttpResponse(status=412)

    body = util.getBody(request)

    if LoginUser.objects.filter(user_id=body.get("user_id"), password=body.get("password"), site_id ='1').exists():
        return util.return_header(200)
    else:
        return util.return_header(401)
