from django.contrib import admin

# Register your models here.
from .models import AccountInfo,UserInfo,CarInfo,CarMinuteRecord,CarDriveRecord,Information,WarnInfomation

admin.site.register(AccountInfo)
admin.site.register(UserInfo)
admin.site.register(CarInfo)
admin.site.register(CarDriveRecord)
admin.site.register(WarnInfomation)

