
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from Config.case_config import photo_url


class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"

    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     print(created)
#     if created:
#         print(instance)
#         Token.objects.create(user=instance)


class UserJob(BaseTable):

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位管理'

    id = models.AutoField(primary_key=True)
    job_name = models.CharField('职位名称', max_length=50, null=False, blank=False)
    job_code = models.CharField('职位Code', max_length=128, null=False, blank=False)
    desc = models.TextField('职位说明', null=True, blank=True)

    def __unicode__(self):
        return self.job_name

    def __str__(self):
        return self.job_name


# ==================扩展用户====================================
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户', related_name='user')
    phone = models.CharField(max_length=11, default='12345678901', null=True, blank=True, verbose_name='手机号')
    photo = models.ImageField(verbose_name="头像", null=True, blank=True, upload_to=photo_url + '/', default=photo_url + '/img.jpg')
    job = models.ForeignKey(UserJob, on_delete=models.CASCADE, verbose_name='职位')
    openid = models.CharField(verbose_name='应用唯一标识', default=0, max_length=50)
    unionid = models.CharField(verbose_name='企业唯一标识', default=0, max_length=50)
    testlink_key = models.CharField(verbose_name="testlink_Key", null=True, blank=True, max_length=1024)
    testlink_name = models.CharField(verbose_name="testlink用户名", null=True, blank=True, max_length=1024)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.phone


class AuthorityManagement(BaseTable):

    class Meta:
        verbose_name = '权限管理'
        verbose_name_plural = '权限管理'

    id = models.AutoField(primary_key=True)
    control_name = models.CharField('权限名称', max_length=50, null=False, blank=False)
    control_code = models.CharField('权限Code', max_length=128, null=False, blank=False)
    desc = models.TextField('权限说明', null=True, blank=True)

    def __unicode__(self):
        return self.control_name

    def __str__(self):
        return self.control_name


class JobAuthority(BaseTable):

    class Meta:
        verbose_name = '职位权限'
        verbose_name_plural = '职位权限'

    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(UserJob, on_delete=models.CASCADE, verbose_name='职位', related_name='job')
    authority = models.ForeignKey(AuthorityManagement, on_delete=models.CASCADE, verbose_name='权限', related_name='authority')

    def __unicode__(self):
        return self.authority

    def __str__(self):
        return self.authority
