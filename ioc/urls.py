from django.urls import path

from . import views

urlpatterns = [
    path('',views.ioc,name='ioc'),
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('userinfo',views.userinfo,name='userinfo'),
    path('userinfo/edit', views.userinfo_edit, name='userinfo_edit'),
    path('password',views.password,name="password"),
    path('carinfo',views.carinfo,name='carinfo'),
    path('carinfo/edit/<int:car_id>',views.carinfoedit,name='carinfoedit'),
    # path('speed',views.carspeed,name='carspeed'),
    path('rotation',views.carrotation,name='carrotation'),
    path('fuelremain',views.carfuelremain,name='fuelremain'),
    path('pressure',views.carpressure,name='pressure'),
    path('watertemperature',views.carwatertemp,name='watertemperature'),
    path('drivingrecord/<int:car_id>/',views.cardriveid,name='driverecordid'),
    path('drivinggraph/<int:car_id>',views.cardrivegraphid,name='drivinggraphid'),
    path('evaluation/<int:car_id>',views.carevaluate,name='evaluate'),
    path('position/<int:car_id>',views.gpsposition,name='gpsposition'),
    path('warning',views.userwarning,name='warning'),
    path('warning_ajax',views.warning_ajax,name='warning_ajax'),
    path('warning_add',views.warning_add,name='warning_add'),
    path('regular/<int:car_id>',views.regular,name='regular'),
    path('cardelete/<int:car_id>',views.cardelete,name='cardelete'),

    path('signup_ajax',views.signup_ajax,name='signup_ajax'),
    path('signup_info',views.signup_info,name='signup_info'),
    path('logout',views.logout,name='logout'),
    # path('admin_signup',views.admin_signup,name='admin_signup'),
    # path('admin_signup_res',views.admin_signup_res,name='admin_signup_res'),
]