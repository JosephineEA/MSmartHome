# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Atomcommand(models.Model):
    atomcommandid = models.CharField(db_column='AtomCommandID', primary_key=True, max_length=20)  # Field name made lowercase.
    content = models.CharField(max_length=255)
    furnitureid = models.ForeignKey('Furniture', models.DO_NOTHING, db_column='FurnitureID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AtomCommand'


class Flat(models.Model):
    flatid = models.CharField(db_column='FlatID', primary_key=True, max_length=20)  # Field name made lowercase.
    flatname = models.CharField(db_column='FlatName', max_length=20)  # Field name made lowercase.
    hostid = models.ForeignKey('User', models.DO_NOTHING, db_column='HostID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Flat'


class Furniture(models.Model):
    furnitureid = models.CharField(db_column='FurnitureID', primary_key=True, max_length=20)  # Field name made lowercase.
    furniturename = models.CharField(db_column='FurnitureName', unique=True, max_length=20)  # Field name made lowercase.
    roomid = models.ForeignKey('Room', models.DO_NOTHING, db_column='RoomID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Furniture'


class Furnitureusing(models.Model):
    number = models.AutoField(db_column='Number', primary_key=True)  # Field name made lowercase.
    flatid = models.ForeignKey(Flat, models.DO_NOTHING, db_column='FlatID', blank=True, null=True)  # Field name made lowercase.
    furnitureid = models.ForeignKey(Furniture, models.DO_NOTHING, db_column='FurnitureID', blank=True, null=True)  # Field name made lowercase.
    furnitureroomid = models.CharField(db_column='FurnitureRoomID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    commandcontent = models.CharField(db_column='CommandContent', max_length=200, blank=True, null=True)  # Field name made lowercase.
    commandtype = models.CharField(db_column='CommandType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    time = models.DateTimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    ifexcute = models.CharField(db_column='IfExcute', max_length=1, blank=True, null=True)  # Field name made lowercase.
    flatname = models.ForeignKey(Flat, models.DO_NOTHING, db_column='FlatName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FurnitureUsing'


class Multicommand(models.Model):
    multicommandid = models.CharField(db_column='MultiCommandID', primary_key=True, max_length=20)  # Field name made lowercase.
    multicommandname = models.CharField(db_column='MultiCommandName', max_length=20)  # Field name made lowercase.
    atomcommandid = models.ForeignKey(Atomcommand, models.DO_NOTHING, db_column='AtomCommandID')  # Field name made lowercase.
    steps = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'MultiCommand'


class Role(models.Model):
    roleid = models.CharField(db_column='RoleID', primary_key=True, max_length=20)  # Field name made lowercase.
    rolename = models.CharField(db_column='RoleName', unique=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Role'


class Rolelimites(models.Model):
    number = models.AutoField(db_column='Number', primary_key=True)  # Field name made lowercase.
    roleid = models.ForeignKey(Role, models.DO_NOTHING, db_column='RoleID')  # Field name made lowercase.
    limitsfurnitureid = models.ForeignKey(Furniture, models.DO_NOTHING, db_column='LimitsFurnitureID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RoleLimites'


class Room(models.Model):
    roomid = models.CharField(db_column='RoomID', primary_key=True, max_length=20)  # Field name made lowercase.
    roomname = models.CharField(db_column='RoomName', max_length=20)  # Field name made lowercase.
    flatid = models.ForeignKey(Flat, models.DO_NOTHING, db_column='FlatID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Room'


class User(models.Model):
    userid = models.CharField(db_column='UserId', primary_key=True, max_length=20)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', unique=True, max_length=20, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255, blank=True, null=True)  # Field name made lowercase.
    isadmin = models.CharField(db_column='IsAdmin', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class UserFlatRole(models.Model):
    number = models.AutoField(db_column='Number', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    flatid = models.ForeignKey(Flat, models.DO_NOTHING, db_column='FlatID', blank=True, null=True)  # Field name made lowercase.
    roleid = models.ForeignKey(Role, models.DO_NOTHING, db_column='RoleID')  # Field name made lowercase.
    ifentered = models.CharField(db_column='IfEntered', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User-Flat-Role'
