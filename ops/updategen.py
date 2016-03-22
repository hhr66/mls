#!/usr/bin/env python
#coding=utf-8
import time,os,sys
import comm
import db_connect
from ops.models import *
reload(sys)
sys.setdefaultencoding('utf-8')

data = Mtree.objects.all()
#nodes = {1:0,2:0,3:1,4:5,5:3}
nodes = {}
for i in data:
    nodes[i.id] = i.pid
ids = nodes.keys()
while ids:
    node_list = []
    id = nid = ids.pop()
    while id:
        node_list.append(id)
        pid = nodes[id]
        if pid == 0: node_list.append(pid)
        id = pid
    gen = '_'.join(map(str, reversed(node_list)))
    deep = len(node_list) -1
    Mtree.objects.filter(id=nid).update(gen=gen,deep=deep)

