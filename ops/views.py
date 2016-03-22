#!/usr/bin/env python
#coding=utf-8
import time,os,sys
import random
import json
import urllib
import urllib2
from xpinyin import Pinyin
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib.auth.models import User
from django.template import RequestContext
from mls.comm import *
from ops.models import *
reload(sys)
sys.setdefaultencoding('utf-8')

def index(request):
    if "name" not in request.session: return HttpResponseRedirect('/login')
    userzhname = request.session["name"]
    if "modename" in request.session:
        modename = request.session["modename"]
    else:
        request.session['modename'] = modename = 'hostlist'
    if "treeid" in request.session:
        treeid = request.session["treeid"]
    else:
        request.session['treeid'] = treeid = 1
    return render_to_response('indexnew.html',locals())

def mtree(request):
    #if "name" not in request.session: return HttpResponseRedirect('/login')
    username = request.session["email"].split('@')[0]
    #data = Mtree.objects.all()
    key = 'owner=www'
    data = Mtree.objects.filter(Q(zh_name__contains=key)|Q(tags__contains=key))
    rootids = [row.treeid for row in  Role.objects.filter(roleid__lte=2,username=username)]
    if Role.objects.filter(roleid=0).count() >0: issupper = 1
    zNodes = "["
    for i in data:
        id = i.id
        pid = i.pid
        deepnum = i.deep
        name = i.zh_name
        gen = i.gen.split('_')
        gen = [ int(i) for i in gen]
        showid = 0
        newlist = list(set(rootids).intersection(set(gen)))
        if newlist:
            if deepnum == 4:
                showid = 1
            else:
                showid = 2
        zNodes += "{id:%s,pId:%s,name:'%s',showid:%s}," %(id,pid,name,showid)
    zNodes += "]"
    treeid = 1
    if "treeid" in request.session: treeid = request.session["treeid"]
    return render_to_response('mtree.html',locals())

def delnode(request):
    if "name" not in request.session: return HttpResponseRedirect('/login')
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    pnode = request.GET.get('pnode',)
    if pnode:
        data = Mtree.objects.filter(Q(gen__contains='_%s_' %treeid)|Q(id=treeid))
        treeids = [row.id for row in data]
        data = Host.objects.filter(treeid__in=treeids).order_by('-saltid')
        hosts = [row.saltid for row in data]
        if hosts: return HttpResponse('error')
        Mtree.objects.filter(Q(gen__contains='_%s_' %treeid)|Q(id=treeid)).delete()
    else:
        num = Host.objects.filter(treeid=treeid).count()
        if num > 0: return HttpResponse('error')
        Mtree.objects.filter(id=treeid).delete()
    return HttpResponse('ok')

def editnode(request):
    if "name" not in request.session: return HttpResponseRedirect('/login')
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    zh_name = request.GET.get('name',)
    p = Pinyin()
    en_name = p.get_pinyin(zh_name,'')
    Mtree.objects.filter(id=int(treeid)).update(zh_name=zh_name,en_name=en_name)
    return HttpResponse('ok')

def addnode(request):
    if "name" not in request.session: return HttpResponseRedirect('/login')
    username = request.session["email"].split('@')[0]
    zh_name = request.GET.get('zh_name',)
    pid = request.GET.get('pid',)
    p = Pinyin()
    en_name = p.get_pinyin(zh_name,'')
    pnode = Mtree.objects.get(id=pid)
    pgen = pnode.gen
    pdeep = pnode.deep
    deep = pdeep + 1
    ret = Mtree.objects.create(pid=pid,deep=deep,zh_name=zh_name,en_name=en_name)
    id = ret.id
    gen = pgen + '_' + str(id)
    Mtree.objects.filter(id=id).update(gen=gen)
    #Mtree.objects.filter(id=int(treeid)).delete()
    showid = 2
    if deep == 4: showid = 1
    data = {'id':id,'showid':showid}
    data = json.dumps(data)
    return HttpResponse(data)

def dropnode(request):
    if "name" not in request.session: return HttpResponseRedirect('/login')
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    dtreeid = request.GET.get('dtreeid',)
    pgen = Mtree.objects.get(id=int(dtreeid)).gen
    pdeep = Mtree.objects.get(id=int(dtreeid)).deep
    deep = pdeep + 1
    gen = pgen + '_' + str(treeid)
    Mtree.objects.filter(id=int(treeid)).update(pid=dtreeid,deep=deep,gen=gen)
    return HttpResponse('ok')

def role(request):
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    modename = request.GET.get('modename',)
    #data = {1:['']}
    return render_to_response('role.html',locals())

def hostlist(request):
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    modename = request.GET.get('modename',)
    gen = Mtree.objects.get(id=int(treeid)).gen
    treeids = gen.split('_')
    ret = Role.objects.filter(username=username,treeid__in=treeids)
    if not ret: return HttpResponse('没权限')
    names = [row.zh_name for row in Mtree.objects.filter(id__in=treeids)]
    nodepath = '/' + '/'.join(names)
    return render_to_response('hostlist.html',locals())

def hostmount(request):
    username = request.session["email"].split('@')[0]
    treeid = request.GET.get('treeid',)
    modename = request.GET.get('modename',)
    gen = Mtree.objects.get(id=int(treeid)).gen
    treeids = gen.split('_')
    ret = Role.objects.filter(username=username,treeid__in=treeids)
    if not ret: return HttpResponse('没权限')
    names = [row.zh_name for row in Mtree.objects.filter(id__in=treeids)]
    nodepath = '/' + '/'.join(names)
    return render_to_response('hostmount.html',locals())
        
def main(request):
    username = request.session["email"].split('@')[0]    
    treeid = 1
    if "treeid" in request.session: treeid = request.session["treeid"]
    gen = Mtree.objects.get(id=int(treeid)).gen
    treeids = gen.split('_')
    ret = Role.objects.filter(username=username,treeid__in=treeids)
    if not ret: return HttpResponse('没权限')
    #response = urllib2.urlopen(get_hosts_api+str(treeid), timeout=10)
    #data = json.loads(response.read())['data']['hostIp']
    data = Mtree.objects.filter(Q(gen__contains='_%s_' %treeid)|Q(id=treeid))
    treeids = [row.id for row in data]
    data = Host.objects.filter(treeid__in=treeids).order_by('-saltid') 
    hosts = [row.saltid for row in data]
    return render_to_response('main.html',locals())    

def saltcmd(request):
    cmd = request.POST.get('cmd',)
    hosts = request.POST.get('hosts',)
    api_url = 'http://saltapibj.main.meiliworks.com/'
    params = {'eauth': 'pam', 'username': 'huironghuang', 'password': '123456'}
    encode = urllib.urlencode(params)
    obj = urllib.unquote(encode)
    headers = {'X-Auth-Token':''}
    url = api_url + 'login'
    req = urllib2.Request(url, obj, headers)
    opener = urllib2.urlopen(req)
    content = json.loads(opener.read())
    token = content['return'][0]['token']
    headers = {'X-Auth-Token'   : token}
    params = {'tgt':hosts,'client':'local','fun':'cmd.run','arg':cmd,'expr_form':'list'}
    #params = {'tgt':'yz-seo-01.meilishuo.com,yz-snake-01.meilishuo.com','client':'local','fun':'cmd.run','arg':'date','expr_form':'list'}
    encode = urllib.urlencode(params)
    obj = urllib.unquote(encode)
    req = urllib2.Request(api_url, obj, headers)
    opener = urllib2.urlopen(req)
    data = json.loads(opener.read())
    hosts = hosts.split(',')
    errhosts = list(set(hosts).difference(set(data['return'][0].keys())))
    total = len(hosts)
    errnum = len(errhosts)
    execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(errhosts))
    datas = {"execerr":execerr,"data":data['return'][0]}
    datas = json.dumps(datas)
    return HttpResponse(datas)

def updatemain(request):
    if "name" not in request.session: return HttpResponse('error')
    treeid = request.session['treeid'] = request.GET.get('treeid',)
    modename = request.session['modename'] = request.GET.get('modename',)
    #mode = request.session['mode'] = request.GET.get('mode',)
    #response = urllib2.urlopen(get_hosts_api+str(treeid), timeout=10)
    #data = json.loads(response.read())['data']['hostIp']
    #data = data.items()
    return HttpResponse('ok')

def login(request):
    #定义SPEED API接口相关信息
    api_host = "http://api.speed.meilishuo.com"
    app_key = "100099"
    callback_url = "http://mls.main.meiliworks.com/speedcallback"
    url = "/oauth/authorize?client_id=" + app_key + "&response_type=code&redirect_uri=" + callback_url
    #拼接URL
    speed_api_url = api_host + url
    return HttpResponseRedirect(speed_api_url)
def logout(request):
    del request.session['name'] 
    del request.session['treeid'] 
    del request.session['modename'] 
    return HttpResponseRedirect('/login')

#SPEED API回调接口方法
def speedcallback(request):
    #获取SPEED API返回的CODE值
    code = request.GET.get('code',)
    #定义SPEED API接口相关信息
    api_host = "http://api.speed.meilishuo.com"
    #获取授权过的Access Token的URL
    url = "/oauth/access_token"
    app_key = "100099"
    client_secret = "3d523612ecee8dc62921f8ef1314814a"
    #拼接URL
    speed_api_url = api_host + url
    data = {'client_id':app_key,'client_secret':client_secret,'grant_type':'authorization_code','redirect_uri=':'SPEED_CALLBACK_URL','code':code}
    req = urllib2.Request(speed_api_url)
    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    response = opener.open(req, data) 
    data = json.loads(response.read())
    if data['code'] == 200:
        #获取access_token的值并返回
        access_token = data['access_token']
        #验证access_token是否有效
        #定义检测 Access Token是否有效的URL
        url = "/oauth/statuses"
        #拼接URL
        speed_api_url = api_host + url
        #设置post数据
        data = {"client_id":app_key,"access_token":access_token}
        req = urllib2.Request(speed_api_url)
        data = urllib.urlencode(data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, data)
        data = json.loads(response.read())
        if data['code'] == 200:
            #将用户数据保存至SESSION
            request.session["name"] = data['data']['name']
            request.session["email"] = data['data']['mail']
            request.session["speed_uid"] = data['data']['id']
            return HttpResponseRedirect('/')
        else:
            return HttpResponse("对不起，您的token值无效，请联系管理员")
    else:
        return HttpResponse("SPPED API返回数据异常")
def ajax_host(request):
    treeid = request.session["treeid"]
    data = Mtree.objects.filter(Q(gen__contains='_%s_' %treeid)|Q(id=treeid))
    treeids = [row.id for row in data]
    data = Host.objects.filter(treeid__in=treeids).order_by('-saltid')
    L = []
    datas = {}
    for i in data:
        L.append([i.ip,i.hostname,i.saltid])
    datas['data'] = L
    return HttpResponse(json.dumps(datas))
def test(request):
    return render_to_response('test.html',locals())
