from django.conf.urls import patterns, include, url

from django.contrib import admin
import ops
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mls.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','ops.views.index',name='index'),
    url(r'^index/','ops.views.index',name='index'),
    url(r'^mtree/','ops.views.mtree',name='mtree'),
    url(r'^delnode','ops.views.delnode',name='delnode'),
    url(r'^editnode','ops.views.editnode',name='editnode'),
    url(r'^addnode','ops.views.addnode',name='addnode'),
    url(r'^dropnode','ops.views.dropnode',name='dropnode'),
    url(r'^hostlist','ops.views.hostlist',name='hostlist'),
    url(r'^hostmount','ops.views.hostmount',name='hostmount'),
    url(r'^role','ops.views.role',name='role'),
    url(r'^test/','ops.views.test',name='test'),
    url(r'^ajax_host','ops.views.ajax_host',name='ajax_host'),
    url(r'^login/','ops.views.login',name='login'),
    url(r'^logout/','ops.views.logout',name='logout'),
    url(r'^speedcallback/','ops.views.speedcallback',name='speedcallback'),
    url(r'^updatemain','ops.views.updatemain',name='updatemain'),
    url(r'^main','ops.views.main',name='main'),
    url(r'^saltcmd','ops.views.saltcmd',name='saltcmd'),
)
