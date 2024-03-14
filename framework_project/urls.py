"""framework_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path,include
from myApp import views
from myApp.views import LoginView

urlpatterns = [


    path("login/",LoginView.as_view()),
    path("signup/",views.SignUpView),
    path("logout/",views.logoutAdmin),
    path("flat/list/",views.flatList),
    path("flat/option/",views.flatOption),
    path("flat/del/",views.flatDel),
    path("room/list/", views.RoomList),
    path("room/option/", views.RoomOption),
    path("room/del/", views.RoomDel),
    path("furniture/list/", views.FurnitureList),
    path("furniture/option/", views.FurnitureOption),
    path("furniture/del/", views.FurnitureDel),
    path("role/list/", views.RoleList),
    path("role/option/", views.RoleOption),
    path("role/del/", views.RoleDel),
    path("user/flat/list/", views.UserFlatList),
    path("user/flat/agree/", views.UserAgree),
    path("user/flat/edit/", views.UserFlatRoleEdit),
    path("atom/list/", views.AtomCommandList),
    path("multi/list/", views.MulticommandList),
    path("role/limit/list/", views.role_limit_list),
    path("role/limit/del/", views.RoleLimitDel),
    path("atom/option/", views.AtomCommandOption),
    path("role/limit/option/", views.RoleLimitOption),
    path("multi/del/", views.MulticommandDel),
    path("mutli/option/", views.MulticommandOption),
    path("atom/del/", views.AtomCommandDel),
    path("apply/flat/", views.ApplayFlat),
    path("comannd/list/", views.CommandList),
    path("use/comand/",views.UseCommandView),
    path("use/comand/list/",views.UseCommandList),
    path("api/room/list/",views.RoomListApiiew),
    path("api/furn/list/",views.FurnitureApiiew),
    path("api/multi/list/",views.multiApiiew),

    path("",views.index),

]
