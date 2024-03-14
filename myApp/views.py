import datetime

from django.db.models import Q
from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from django.views import View
from django.http.response import JsonResponse

from myApp.models import User, Flat, Room, Role, UserFlatRole, Furniture, Atomcommand, Multicommand, Rolelimites, \
    Furnitureusing
import json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required  # 验证用户是否登录


def logoutAdmin(request):
    logout(request)
    return redirect("/login")


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', locals())

    def post(self, request):
        no = request.POST.get("no", None)  #
        password = request.POST.get("password", None)  # 验证码答案
        user=User.objects.filter(userid=no).first()
        if user is None:
            msg = "用户不存在，登陆失败"

        else:
            if user.password==password:
                request.session['userinfo'] = {"id": user.userid, 'username': user.username, 'type': user.isadmin}
                return redirect("/")
            else:
                msg = "密码不正确，登陆失败"
        return render(request, "login.html", locals())


def SignUpView(request):
    if request.method == "GET":
        return render(request, 'signup.html', locals())
    elif request.method == "POST":
        no = request.POST.get("no", None)
        password = request.POST.get("password", None)
        password2 = request.POST.get("password2", None)
        name = request.POST.get("name", None)
        if password != password2:
            msg = "两次密码不一致"
            return render(request, 'signup.html', locals())
        user = User.objects.filter(userid=no).first()
        if user is not None:
            msg = "该用户id已经存在"
            return render(request, 'signup.html', locals())
        user = User.objects.filter(username=name).first()
        if user is not None:
            msg = "该账号已经存在"
            return render(request, 'signup.html', locals())
        user = User.objects.create(username=name, password=password,userid=no,isadmin=0)
        return redirect("/login/")

def index(request):
    return render(request,'index.html')
# 公寓列表
def flatList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        if page is None or page == "":
            page = 1
        userFlatRoles=UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values("flatid_id").all()
        filterInfo=[x['flatid_id'] for x in userFlatRoles]
        flat = Flat.objects.filter(flatid__in=filterInfo).order_by("-flatid")
        paginator = Paginator(flat, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'flat_list.html', locals())
#删除公寓
def flatDel(request):
    flatid = request.GET.get("flatid")
    try:
        UserFlatRole.objects.filter(flatid_id=flatid).delete()
        Flat.objects.filter(flatid=flatid).delete()
    except:
        return redirect("/flat/list/?msg={}".format("该公寓正在使用，不可删除"))
    return redirect("/flat/list/")
# #
#修改公寓信息
def flatOption(request):
    flatid = request.GET.get("flatid")
    if flatid is not None and flatid != "":
        flat = Flat.objects.filter(flatid=flatid).first()
    users=User.objects.all()

    if request.method == "GET":
        return render(request, 'flat_option.html', locals())

    FlatNo = request.POST.get("FlatNo")
    FlatName = request.POST.get("FlatName")
    HostID = request.POST.get("HostID")


    if flatid is not None and flatid != "":
        # 校验信息是否完整

        if FlatName is None or HostID is None:
            msg="信息不完备，录入失败"
            return render(request, 'flat_option.html', locals())
        # 修改用户信息
        pre_hostid=flat.hostid
        flat.flatname=FlatName
        flat.hostid_id=HostID
        flat.save()
        # 判断之前的用户是否是房主，不是的话admin字段更新为普通用户
        num = Flat.objects.filter(hostid_id=pre_hostid).count()
        if num <= 0:
            User.objects.filter(userid=pre_hostid).update(isadmin=0)

    else:
        # 校验信息是否完整
        if FlatNo is None or FlatName is None or HostID is None:
            msg="信息不完备，录入失败"
            return render(request, 'flat_option.html', locals())
        # 判断该编号是否存在
        flat2=Flat.objects.filter(flatid=FlatNo).first()
        if flat2 is not None:
            msg="该编号已经存在"
            return render(request,'flat_option.html',locals())
        #新增一条公寓记录
        Flat.objects.create(hostid_id=HostID, flatname=FlatName,flatid=FlatNo)
    #     增加一条权限记录
    role=Role.objects.filter(rolename="admin").first()
    ufr=UserFlatRole.objects.filter(userid=HostID, flatid=FlatNo).first()
    if ufr is None:
        UserFlatRole.objects.create(userid_id=HostID,flatid_id=FlatNo,roleid=role)
    else:
        ufr.roleid=role
        ufr.save()
    User.objects.filter(userid=HostID).update(isadmin=1)
    return redirect("/flat/list/")



# 公寓房间列表
def RoomList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        if page is None or page == "":
            page = 1
        userFlatRoles=UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values("flatid_id").all()
        filterInfo=[x['flatid_id'] for x in userFlatRoles]
        room = Room.objects.filter(flatid_id__in=filterInfo).order_by("-flatid")
        paginator = Paginator(room, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'room_list.html', locals())
#删除房间
def RoomDel(request):
    roomid = request.GET.get("roomid")
    try:
        Furniture.objects.filter(roomid_id=roomid).delete()

        Room.objects.filter(roomid=roomid).delete()
    except:
        return redirect("/room/list/?msg={}".format("该房间正在使用，不可删除"))
    return redirect("/room/list/")
# #
#修改房间信息
def RoomOption(request):
    roomid = request.GET.get("roomid")
    if roomid is not None and roomid != "":
        room = Room.objects.filter(roomid=roomid).first()
    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values("flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    flats=Flat.objects.filter(flatid__in=filterInfo)

    if request.method == "GET":
        return render(request, 'room_option.html', locals())

    roomNo = request.POST.get("roomno")
    roomName = request.POST.get("roomname")
    flatid = request.POST.get("flatid")


    if roomid is not None and roomid != "":
        # 校验信息是否完整

        if roomName is None or flatid is None:
            msg="信息不完备，录入失败"
            return render(request, 'room_option.html', locals())
        # 修改房间信息
        room2=Room.objects.filter(roomname=roomName).filter(~Q(flatid_id=flatid)).first()
        if room2 is not None:
            msg="房间名已经存在"
            return render(request,'room_option.html',locals())
        room.roomName=roomName
        room.flatid.flatid=flatid
        room.save()

    else:
        # 校验信息是否完整
        if roomNo is None or roomName is None or flatid is None:
            msg="信息不完备，录入失败"
            return render(request, 'room_option.html', locals())
        # 判断该编号是否存在
        room2=Room.objects.filter(roomid=roomNo).first()
        if room2 is not None:
            msg="该编号已经存在"
            return render(request,'room_option.html',locals())
        room2=Room.objects.filter(roomname=roomName).first()
        if room2 is not None:
            msg="房间名已经存在"
            return render(request,'room_option.html',locals())
        #新增一条房间记录
        Room.objects.create(roomname=roomName, flatid_id=flatid,roomid=roomNo)

    return redirect("/room/list/")

#家具列表
#
def FurnitureList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        if page is None or page == "":
            page = 1
        userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
            "flatid_id").all()
        filterInfo = [x['flatid_id'] for x in userFlatRoles]
        filterInfo.append(0)
        room = Furniture.objects.filter(roomid__flatid_id__in=filterInfo).order_by("-furnitureid")
        paginator = Paginator(room, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'furniture_list.html', locals())
#删除家具
def FurnitureDel(request):
    furnitureid = request.GET.get("furnitureid")
    try:
        Furniture.objects.filter(furnitureid=furnitureid).delete()
    except:
        return redirect("/furniture/list/?msg={}".format("该家具正在使用，不可删除"))
    return redirect("/furniture/list/")
# #
#修改家具信息
def FurnitureOption(request):
    furnitureid = request.GET.get("furnitureid")
    if furnitureid is not None and furnitureid != "":
        furniture = Furniture.objects.filter(furnitureid=furnitureid).first()
    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values("flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    rooms=Room.objects.filter(flatid_id__in=filterInfo).all()

    if request.method == "GET":
        return render(request, 'furniture_option.html', locals())

    furnitureNo = request.POST.get("furnitureno")
    furnitureName = request.POST.get("furnitureName")
    roomid = request.POST.get("roomid")

    if furnitureid is not None and furnitureid != "":
        # 校验信息是否完整
        if furnitureName is None or roomid is None:
            msg="信息不完备，录入失败"
            return render(request, 'furniture_option.html', locals())
        # 修改家具信息
        furniture2=Furniture.objects.filter(furniturename=furnitureName).filter(~Q(furnitureid=furnitureid)).first()
        if furniture2 is not None:
            msg="该家具名称已经存在"
            return render(request,'furniture_option.html',locals())
        furniture.furniturename=furnitureName
        furniture.roomid_id=roomid
        furniture.save()

    else:
        # 校验信息是否完整
        if furnitureNo is None or furnitureName is None or roomid is None:
            msg="信息不完备，录入失败"
            return render(request, 'furniture_option.html', locals())
        # 判断该编号是否存在
        furniture=Furniture.objects.filter(furnitureid=furnitureNo).first()
        if furniture is not None:
            msg="该编号已经存在"
            return render(request,'furniture_option.html',locals())
        furniture=Furniture.objects.filter(furniturename=furnitureName).first()
        if furniture is not None:
            msg="该家具名称已经存在"
            return render(request,'furniture_option.html',locals())
        #新增一条房间记录
        Furniture.objects.create(furnitureid=furnitureNo, furniturename=furnitureName,roomid_id=roomid)

    return redirect("/furniture/list/")




#角色列表
#
def RoleList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        msg=request.GET.get("msg")
        if page is None or page == "":
            page = 1

        roles = Role.objects.all().order_by("-roleid")
        paginator = Paginator(roles, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'role_list.html', locals())
#删除角色
def RoleDel(request):
    id = request.GET.get("id")
    try:
        Role.objects.filter(roleid=id).delete()
    except:
        return redirect("/role/list/?msg={}".format("该角色正在使用，不可删除"))
    return redirect("/role/list/")
# #
#修改角色信息
def RoleOption(request):
    id = request.GET.get("id")
    if id is not None and id != "":
        role = Role.objects.filter(roleid=id).first()

    if request.method == "GET":
        return render(request, 'role_option.html', locals())

    roleid = request.POST.get("roleid")
    rolename = request.POST.get("rolename")

    if id is not None and id != "":
        # 校验信息是否完整
        if rolename is None:
            msg="信息不完备，录入失败"
            return render(request, 'role_option.html', locals())
        # 修改家具信息
        role2=Role.objects.filter(rolename=rolename).filter(~Q(roleid=roleid)).first()
        if role2 is not None:
            msg="该角色名称已经存在"
            return render(request,'role_option.html',locals())
        role.rolename=rolename
        role.save()

    else:
        # 校验信息是否完整
        if roleid is None or rolename is None:
            msg="信息不完备，录入失败"
            return render(request, 'role_option.html', locals())
        # 判断该编号是否存在
        role=Role.objects.filter(roleid=roleid).first()
        if role is not None:
            msg="该编号已经存在"
            return render(request,'role_option.html',locals())
        role=Role.objects.filter(rolename=rolename).first()
        if role is not None:
            msg="该角色名称已经存在"
            return render(request,'role_option.html',locals())
        #新增一条角色
        Role.objects.create(roleid=roleid, rolename=rolename)

    return redirect("/role/list/")



#角色列表
#
def UserFlatList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        msg=request.GET.get("msg")
        flatid=request.GET.get("flatid",None)
        if page is None or page == "":
            page = 1
        flatlist=Flat.objects.filter(hostid_id=request.session['userinfo']['id'])
        if flatid is None:
            flatid=flatlist.first().flatid
        userFlatRoleList = UserFlatRole.objects.filter(flatid=flatid).all()
        paginator = Paginator(userFlatRoleList, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'user_flat_list.html', locals())

#同意入户
def UserAgree(request):
    if request.method == "GET":
        number=request.GET.get("id")
        flatid=request.GET.get("flatid")
        flag=request.GET.get("flag")
        userFlatRole=UserFlatRole.objects.filter(number=number).first()
        userFlatRole.ifentered=flag
        userFlatRole.save()
        return redirect('/user/flat/list/?flatid={}'.format(flatid))


def UserFlatRoleEdit(request):
    roles=Role.objects.all()
    number = request.GET.get("id")
    flatid = request.GET.get("flatid",None)
    userFlatRole = UserFlatRole.objects.filter(number=number).first()
    if request.method=="GET":
        return render(request,'user_flat_option.html',locals())
    roleid=request.POST.get("roleid")

    userFlatRole.roleid_id=roleid
    userFlatRole.save()

    role=Role.objects.get(roleid=roleid)
    user = User.objects.filter(userid=userFlatRole.userid.userid).first()
    if role.rolename=="admin":
        user.isadmin=1
        user.save()
    else:
        userFlatRole = UserFlatRole.objects.filter(userid=userFlatRole.userid).filter(roleid__rolename="admin").count()
        if userFlatRole==0:
            user.isadmin=0
            user.save()

    return redirect('/user/flat/list/?flatid={}'.format(flatid))


#指令列表
#
def AtomCommandList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        msg=request.GET.get("msg")
        if page is None or page == "":
            page = 1
        userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
                "flatid_id").all()
        filterInfo = [x['flatid_id'] for x in userFlatRoles]

        atomList = Atomcommand.objects.filter(furnitureid__roomid__flatid__in=filterInfo).all()
        paginator = Paginator(atomList, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'atom_list.html', locals())
#删除角色
def  AtomCommandDel(request):
    id = request.GET.get("id")
    try:
        Atomcommand.objects.filter(atomcommandid=id).delete()
    except:
        return redirect("/atom/list/?msg={}".format("该指令正在使用，不可删除"))
    return redirect("/atom/list/")


#修改角色信息
def  AtomCommandOption(request):
    id = request.GET.get("id")
    furniturelist=Furniture.objects.all()
    if id is not None and id != "":
        atom = Atomcommand.objects.filter(atomcommandid=id).first()
    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
        "flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    furnitureList = Furniture.objects.filter(roomid__flatid__in=filterInfo).all()
    dict1={}
    for i in furnitureList:
        key=i.roomid.flatid.flatid+"-"+i.roomid.flatid.flatname+"-"+i.roomid.roomid+"-"+i.roomid.roomname
        if key not in dict1.keys():
            dict1[key]=set()
        dict1[key].add(i.furnitureid+"-"+i.furniturename)
    furnitureList2=[]
    for key,value in dict1.items():
        info=key.split("-")
        dict2={}
        dict2["flatid"]=info[0]
        dict2["flatname"]=info[1]
        dict2["roomid"]=info[2]
        dict2["roomname"]=info[3]
        list2=[]
        for x in value:
            x=x.split("-")
            list2.append({"name":x[1],"id":x[0]})
        dict2["furnlist"]=list2
        furnitureList2.append(dict2)
    if request.method == "GET":
        return render(request, 'atom_option.html', locals())



    furnitureid = request.POST.get("furnitureid")
    content = request.POST.get("content")
    atomid = request.POST.get("atomid")

    if id is not None and id != "":
        # 校验信息是否完整
        if furnitureid is None and content is None:
            msg="信息不完备，录入失败"
            return render(request, 'atom_option.html', locals())
        atom = Atomcommand.objects.filter(atomcommandid=id).first()

        atom.content=content
        f=Furniture.objects.get(furnitureid=furnitureid)

        atom.furnitureid=f
        atom.save()

    else:
        # 校验信息是否完整
        if furnitureid is None or content is None and atomid is None:
            msg="信息不完备，录入失败"
            return render(request, 'atom_option.html', locals())
        # 判断该编号是否存在
        atom=Atomcommand.objects.filter(atomcommandid=atomid).first()
        if atom is not None:
            msg="该编号已经存在"
            return render(request,'atom_option.html',locals())

        Atomcommand.objects.create(atomcommandid=atomid, furnitureid_id=furnitureid,content=content)

    return redirect("/atom/list/")


#指令列表
#
def MulticommandList(request):
    if request.method == "GET":
        page = request.GET.get("page")
        msg=request.GET.get("msg")
        if page is None or page == "":
            page = 1
        userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
                "flatid_id").all()
        filterInfo = [x['flatid_id'] for x in userFlatRoles]

        multiList = Multicommand.objects.filter(atomcommandid__furnitureid__roomid__flatid__in=filterInfo).order_by("steps").all()
        multiLists=[]
        multiDict1={}
        for i in multiList:
            if i.multicommandid+"-"+i.multicommandname not in multiDict1.keys():
                multiDict1[i.multicommandid+"-"+i.multicommandname]=[]
            multiDict1[i.multicommandid +"-"+ i.multicommandname].append(i)

        for key,value in multiDict1.items():

            info=key.split("-")
            dict1={}
            dict1['id']=info[0]
            dict1['name']=info[1]
            dict1["atomList"]=value
            multiLists.append(dict1)

        paginator = Paginator(multiLists, 10)
        page = paginator.page(page)  # 传递当前页的实例对象到前端
        return render(request, 'multi_list.html', locals())


# # #删除符合角色
def  MulticommandDel(request):
    id = request.GET.get("id")
    try:
        Multicommand.objects.filter(number=id).delete()
    except:
        return redirect("/multi/list/?msg={}".format("该指令正在使用，不可删除"))
    return redirect("/multi/list/")

# # #修改角色信息
def  MulticommandOption(request):
    id = request.GET.get("id")
    multi = Multicommand.objects.filter(number=id).first()

    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
        "flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    # 查询所有的原子指令
    atomList = Atomcommand.objects.filter(furnitureid__roomid__flatid__in=filterInfo).all()

    multiList = Multicommand.objects.filter(atomcommandid__furnitureid__roomid__flatid__in=filterInfo).all()
    multi1List = []
    multi2List = []
    filterList=[]
    for i in multiList:

        if i.multicommandid not in multi1List:
            multi1List.append(i.multicommandid)
            multi2List.append(i.multicommandname)

    if request.method == "GET":
        print(multi)
        return render(request, 'multi_option.html', locals())
    multicommandid = request.POST.get("multicommandid")
    multicommandname = request.POST.get("multicommandname")
    atomcommandid = request.POST.get("atomcommandid")
    steps = request.POST.get("steps")
    if id is not None and id != "":
#         # 校验信息是否完整
        if multicommandname is None or atomcommandid is None or steps is None or multicommandid is None:
            msg="信息不完备，录入失败"
            return render(request, 'multi_option.html', locals())
        multi = Multicommand.objects.filter(number=id).first()
        multi.multicommandname=multicommandname
        multi.atomcommandid_id=atomcommandid
        multi.steps=steps
        multi.save()
#
    else:
#         # 校验信息是否完整
        if multicommandname is None or atomcommandid is None or steps is None or multicommandid is None:
            msg="信息不完备，录入失败"
            return render(request, 'multi_option.html', locals())
        Multicommand.objects.create(multicommandid=multicommandid, multicommandname=multicommandname,atomcommandid_id=atomcommandid,steps=steps)
#
    return redirect("/multi/list/")

def role_limit_list(request):
    if request.method == "GET":
        page = request.GET.get("page")
        msg = request.GET.get("msg")
        if page is None or page == "":
            page = 1


        roleslimites = Rolelimites.objects.all()



        paginator = Paginator(roleslimites, 10)
        page = paginator.page(page)
        return render(request, 'role_limit_list.html', locals())

def  RoleLimitDel(request):
    id = request.GET.get("id")
    try:
        Rolelimites.objects.filter(number=id).delete()
    except:
        return redirect("/role/limit/list/?msg={}".format("该指令正在使用，不可删除"))
    return redirect("/role/limit/list/")


# # #修改角色信息
def  RoleLimitOption(request):

    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).values(
        "flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    furnitureList = Furniture.objects.filter(roomid__flatid__in=filterInfo).all()
    dict1 = {}
    for i in furnitureList:
        key = i.roomid.flatid.flatid + "-" + i.roomid.flatid.flatname + "-" + i.roomid.roomid + "-" + i.roomid.roomname
        if key not in dict1.keys():
            dict1[key] = set()
        dict1[key].add(i.furnitureid + "-" + i.furniturename)
    furnitureList2 = []
    for key, value in dict1.items():
        info = key.split("-")
        dict2 = {}
        dict2["flatid"] = info[0]
        dict2["flatname"] = info[1]
        dict2["roomid"] = info[2]
        dict2["roomname"] = info[3]
        list2 = []
        for x in value:
            x = x.split("-")
            list2.append({"name": x[1], "id": x[0]})
        dict2["furnlist"] = list2
        furnitureList2.append(dict2)
    roles=Role.objects.all()

    if request.method == "GET":
        return render(request, 'role_limit_option.html', locals())
    roleid = request.POST.get("roleid")
    limitsfurnitureid = request.POST.get("limitsfurnitureid")
#         # 校验信息是否完整
    if roleid is None or limitsfurnitureid is None :
        msg="信息不完备，录入失败"
        return render(request, 'role_limit_option.html', locals())
    Rolelimites.objects.create(roleid_id=roleid, limitsfurnitureid_id=limitsfurnitureid)
#
    return redirect("/role/limit/list/")


def ApplayFlat(request):
    flatlst=Flat.objects.filter(~Q(flatname="默认"))
    roleList=Role.objects.all()
    if request.method=="GET":
        return render(request,'apply_option.html',locals())
    userid=request.POST.get("userid")
    roleid=request.POST.get("roleid")
    flatid=request.POST.get("flatid")
    count=UserFlatRole.objects.filter(flatid_id=flatid).filter(userid_id=userid).count()
    if count>0:
        msg="该公寓已经申请过了，不可再次申请"
        return render(request,'apply_option.html',locals())
    UserFlatRole.objects.create(flatid_id=flatid,userid_id=userid,roleid_id=roleid,ifentered=0)
    msg = "您的申请已经提交"
    return render(request, 'apply_option.html', locals())

def CommandList(request):
    page = request.GET.get("page")
    msg = request.GET.get("msg")
    if page is None or page == "":
        page = 1
    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).filter(ifentered=1).values(
        "flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    flatList = Flat.objects.filter(flatid__in=filterInfo).all()


    if len(flatList)==0:
        return render(request,'command_list.html',locals())
    flatid=request.GET.get("flatid")
    if flatid is None or flatid!="":
        flatid=flatList.first().flatid
    multiList = Multicommand.objects.filter(atomcommandid__furnitureid__roomid__flatid=flatid).order_by(
        "steps").all()
    multiLists = []
    multiDict1 = {}
    for i in multiList:
        if i.multicommandid + "-" + i.multicommandname not in multiDict1.keys():
            multiDict1[i.multicommandid + "-" + i.multicommandname] = []
        multiDict1[i.multicommandid + "-" + i.multicommandname].append(i)

    for key, value in multiDict1.items():
        info = key.split("-")
        dict1 = {}
        dict1['id'] = info[0]
        dict1['name'] = info[1]
        dict1["atomList"] = value
        multiLists.append(dict1)

    paginator = Paginator(multiLists, 10)
    page = paginator.page(page)  # 传递当前页的实例对象到前端
    return render(request,'command_list.html',locals())

def UseCommandList(request):
    page = request.GET.get("page")
    msg = request.GET.get("msg")
    if page is None or page == "":
        page = 1
    userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).filter(ifentered=1).values(
        "flatid_id").all()
    filterInfo = [x['flatid_id'] for x in userFlatRoles]
    flatList = Flat.objects.filter(flatid__in=filterInfo).all()

    if len(flatList)==0:
        return render(request,'command_list.html',locals())
    flatid=request.GET.get("flatid")
    if flatid is None or flatid!="":
        flatid=flatList.first().flatid
    furnitureusinglist = Furnitureusing.objects.filter(flatid_id=flatid).all()


    paginator = Paginator(furnitureusinglist, 10)
    page = paginator.page(page)  # 传递当前页的实例对象到前端
    return render(request,'use_command_list.html',locals())
def UseCommandView(request):
    if request.method=="GET":
        userFlatRoles = UserFlatRole.objects.filter(userid_id=request.session['userinfo']['id']).filter(ifentered=1).values(
            "flatid_id").all()
        filterInfo = [x['flatid_id'] for x in userFlatRoles]
        flatList = Flat.objects.filter(flatid__in=filterInfo).all()
        return render(request, 'use_command.html', locals())

    roomid=request.POST.get("roomid",None)
    flatid=request.POST.get("flatid",None)
    multiid=request.POST.get("multiid",None)
    typeid=request.POST.get("typeid",None)
    content=request.POST.get("content",None).strip()
    furnid=request.POST.get("furnid",None)
    userFlatRole=UserFlatRole.objects.filter(flatid_id=flatid).filter(userid_id=request.session['userinfo']['id']).first()
    limitlist=[]
    if userFlatRole is not None:
        rolelimites=Rolelimites.objects.filter(roleid_id=userFlatRole.roleid).all()
        limitlist=[x.limitsfurnitureid.furnitureid for x in rolelimites]
    if roomid is None or flatid is None or typeid is None or furnid is None:
        return JsonResponse({"code":500,"msg":"指令下载失败"})
    if typeid=="multi":
        multicommand=Multicommand.objects.filter(multicommandid=multiid).all()
        for i in multicommand:
            if i.atomcommandid.furnitureid.furnitureid in limitlist:
                Furnitureusing.objects.create(flatid_id=flatid, furnitureid_id=i.atomcommandid.furnitureid.furnitureid, furnitureroomid=roomid,
                                              commandcontent=i.atomcommandid.content, commandtype=typeid, time=datetime.datetime.now(),
                                              ifexcute=0)
            else:
                Furnitureusing.objects.create(flatid_id=flatid, furnitureid_id=i.atomcommandid.furnitureid.furnitureid, furnitureroomid=roomid,
                                              commandcontent=i.atomcommandid.content, commandtype=typeid,
                                              time=datetime.datetime.now(),
                                              ifexcute=1)
        return JsonResponse({"code": 200, "msg": "下载指令成功"})
    else:
        if str(furnid)  in limitlist:
            Furnitureusing.objects.create(flatid_id=flatid, furnitureid_id=furnid, furnitureroomid_id=roomid,
                                          commandcontent=content, commandtype=typeid, time=datetime.datetime.now(),
                                          ifexcute=0)
            return JsonResponse({"code": 500, "msg": "禁止使用该指令"})
        Furnitureusing.objects.create(flatid_id=flatid,furnitureid_id=furnid,furnitureroomid=roomid,commandcontent=content,commandtype=typeid,time=datetime.datetime.now(),ifexcute=1)

        return JsonResponse({"code": 200, "msg": "下载指令成功"})


def RoomListApiiew(request):
    flatid=request.GET.get("flatid").strip()

    roomlist=Room.objects.filter(flatid_id=flatid).all()

    data=[]
    for i in roomlist:

        data.append(i.scheme_one())

    return JsonResponse({"data":data})

def FurnitureApiiew(request):
    roomid=request.GET.get("roomid")
    furnitureList=Furniture.objects.filter(roomid_id=roomid).all()
    data=[]
    for i in furnitureList:
        data.append(i.scheme_one())
    return JsonResponse({"data":data})

def multiApiiew(request):
    flatid=request.GET.get("flatid")
    multiList = Multicommand.objects.filter(atomcommandid__furnitureid__roomid__flatid_id=flatid).all()
    data=[]
    filterList=[]
    for i in multiList:
        if i.multicommandid not in filterList:

            data.append(i.scheme_one())
            filterList.append(i.multicommandid)


    return JsonResponse({"data": data})

