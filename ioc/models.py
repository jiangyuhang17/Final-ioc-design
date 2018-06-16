from django.db import models

# Create your models here.
class AccountInfo(models.Model):
    account = models.CharField(max_length=50,verbose_name="账号")
    password = models.CharField(max_length=100,verbose_name="密码")
    # 0 represents admin,1 represents normal user
    actype = models.IntegerField(verbose_name="账号权限")
    userinfo_status = models.BooleanField(default=False,verbose_name="用户信息是否填入")

    class Meta:
        db_table = "accountinfo"

class UserInfo(models.Model):
    uname = models.CharField(max_length=50,verbose_name="姓名")
    usex = models.BooleanField(verbose_name="性别")
    ubirth_year = models.IntegerField(verbose_name="出身年")
    ubirth_month = models.IntegerField(verbose_name="出身月")
    udrive_year = models.IntegerField(verbose_name="驾龄")
    uaddress = models.CharField(max_length=100,verbose_name="地址")
    uphone = models.CharField(max_length=20,verbose_name="手机")
    uevaluation = models.IntegerField(default=100,verbose_name="安全行为评估")
    accountinfo = models.OneToOneField(AccountInfo,on_delete=models.CASCADE,verbose_name="用户对应账号")

    class Meta:
        db_table = "userinfo"

class CarInfo(models.Model):
    cid = models.CharField(max_length=50,verbose_name="牌照")
    cbrand = models.CharField(max_length=20,verbose_name="品牌")
    cdisplace = models.FloatField(verbose_name="排量")
    cbirth_year = models.IntegerField(verbose_name="生产年")
    cbirth_month = models.IntegerField(verbose_name="生产月")
    cuse_year = models.IntegerField(verbose_name="初用年")
    cuse_month = models.IntegerField(verbose_name="初用月")

    userinfo = models.ForeignKey(UserInfo,on_delete=models.CASCADE,verbose_name="汽车从属的用户")

    class Meta:
        db_table = "carinfo"

class CarMinuteRecord(models.Model):
    time = models.DateTimeField(verbose_name='时间戳')
    use_status = models.BooleanField(verbose_name="汽车状态")
    # speed = models.FloatField(verbose_name="车速")      #km/h
    rotation = models.IntegerField(verbose_name="转速") #rpm
    mileage = models.FloatField(verbose_name="总里程")    #km
    fuel = models.FloatField(verbose_name="油量")       # %
    pressure = models.FloatField(verbose_name="胎压")   # bar
    watertemp = models.FloatField(verbose_name="水温")  # ℃

    carinfo = models.ForeignKey(CarInfo,on_delete=models.CASCADE,verbose_name="时刻记录对应汽车")

    class Meta:
        db_table = "carminuterecord"

class CarDriveRecord(models.Model):
    year = models.IntegerField(verbose_name="驾驶年")
    month = models.IntegerField(verbose_name="驾驶月")
    day = models.IntegerField(verbose_name="驾驶天")
    overspeed = models.FloatField(verbose_name="超速均速")
    overcar = models.IntegerField(verbose_name="超车次数")
    rapidac = models.IntegerField(verbose_name="急加速次数")
    rapidde = models.IntegerField(verbose_name="急减速次数")

    carinfo = models.ForeignKey(CarInfo,on_delete=models.CASCADE,verbose_name="驾驶记录对应汽车")

    class Meta:
        db_table = "cardriverecord"

class Information(models.Model):
    car_id = models.IntegerField('车辆id', db_column='car_id')
    longitude = models.FloatField('经度', db_column='longitude', max_length=255)
    latitude = models.FloatField('纬度', db_column='latitude', max_length=255)
    time = models.DateTimeField('时间戳', db_column='time', max_length=255)
    x_range = models.FloatField('x分段', db_column='x_range', max_length=255, null=True)
    y_range = models.FloatField('y分段', db_column='y_range', max_length=255, null=True)
    class Meta:
        db_table = 'GPS_information'

class WarnInfomation(models.Model):
    display = models.IntegerField(verbose_name='是否显示',default=2)#0为忽略，1为已读，2为未读
    color = models.IntegerField(verbose_name='显示颜色')# 0为红色danger,1为黄色warning
    content = models.CharField(max_length=100,verbose_name='警告内容')
    time = models.DateTimeField(verbose_name='时间戳')

    userinfo = models.ForeignKey(UserInfo,on_delete=models.CASCADE,verbose_name="警告对应用户",default='None')

    class Meta:
        db_table = 'WarnInfomation'

