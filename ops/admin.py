from django.contrib import admin

from ops.models import *

class MtreeAdmin(admin.ModelAdmin):
    list_display = ('id','pid','deep','gen','zh_name','en_name','tags','ctime')
class RoleAdmin(admin.ModelAdmin):
    list_display = ('username','treeid','roleid','admin','ctime')
class HostAdmin(admin.ModelAdmin):
    list_display = ('saltid','hostname','ip','sn','os','treeid','status','tags','ctime')
admin.site.register(Mtree,MtreeAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(Host,HostAdmin)
