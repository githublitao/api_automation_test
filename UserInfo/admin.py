from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from UserInfo.models import UserProfile, AuthorityManagement, JobAuthority, UserJob
from api_test.models import ProjectMember


class ProfileInline(admin.StackedInline):
    """
    用户模块扩展
    """
    model = UserProfile
    readonly_fields = ['openid', 'unionid']


class PhoneForm(admin.ModelAdmin):
    fieldsets = ([
                     '手机号', {
            'fields': ('phone', 'photo', 'job')
        }],)


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline, ]

    def save_model(self, request, obj, form, change):
        pro_member = ProjectMember.objects.filter(user=obj.id)
        if len(pro_member):
            pro_member.update(permissionType=obj.user.job)
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserJob)
class UserJobForm(admin.ModelAdmin):
    search_fields = ('job_name', 'job_code', 'desc')
    list_display = ('id', 'job_name', 'job_code', 'desc')
    list_display_links = ('id', 'job_name')
    # list_filter = ('permissionType', 'project', 'user')
    list_per_page = 20
    ordering = ('-id',)


@admin.register(AuthorityManagement)
class AuthorityManagementForm(admin.ModelAdmin):
    search_fields = ('control_name', 'control_code', 'desc')
    list_display = ('id', 'control_name', 'control_code', 'desc')
    list_display_links = ('id', 'control_name')
    # list_filter = ('permissionType', 'project', 'user')
    list_per_page = 20
    ordering = ('-id',)


@admin.register(JobAuthority)
class JobAuthorityForm(admin.ModelAdmin):
    search_fields = ('job', 'authority')
    list_display = ('id', 'job', 'authority')
    list_display_links = ('id', 'authority')
    # list_filter = ('permissionType', 'project', 'user')
    list_per_page = 20
    ordering = ('-id',)
