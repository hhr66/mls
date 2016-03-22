#!/usr/bin/env python
#coding=utf-8
from django.db.models import *
# Create your models here.
class Mtree(Model):
    pid = IntegerField()
    deep = IntegerField()
    gen = CharField(max_length=50)
    zh_name = CharField(max_length=100)
    en_name = CharField(max_length=100)
    tags = CharField(max_length=1000)
    ctime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.en_name

class Role(Model):
    username = CharField(max_length=50)
    roleid = IntegerField()
    treeid = IntegerField()
    admin = CharField(max_length=50)
    ctime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.username

class Host(Model):
    saltid = CharField(max_length=100)
    hostname = CharField(max_length=100)
    ip = CharField(max_length=100)
    sn = CharField(max_length=100)
    os = CharField(max_length=50)
    treeid = IntegerField()
    status = IntegerField()
    tags = CharField(max_length=1000)
    ctime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.saltid

#roleid
#0:超级管理员
#1:OP管理员
#2:OP
#3:QA管理员
#4:RD管理员
#5:QA
#6:RD
#
