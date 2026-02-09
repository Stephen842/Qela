from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSession, IPActivity, BlacklistedIP

# -------------------------------
# User Admin
# -------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'username', 'name', 'is_active',
        'is_verified', 'is_staff', 'is_platform_admin', 'date_joined'
    )
    list_filter = ('is_active', 'is_verified', 'is_staff', 'is_platform_admin')
    search_fields = ('email', 'username', 'name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_platform_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login', 'last_activity', 'account_updated_at', 'deactivated_at')}),
        ('Email updates', {'fields': ('_new_email', 'email_verification_pending')}),
        ('Deactivation', {'fields': ('is_deactivated',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'password1', 'password2', 'is_active', 'is_verified', 'is_platform_admin'),
        }),
    )

# -------------------------------
# UserProfile Admin
# -------------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'gender', 'phone_number', 'created_at')
    search_fields = ('user__email', 'user__username', 'phone_number')
    list_filter = ('country', 'gender', 'created_at')

# -------------------------------
# UserSession Admin
# -------------------------------
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device_type', 'os', 'browser', 'last_active', 'is_active')
    search_fields = ('user__email', 'ip_address', 'user_agent')
    list_filter = ('device_type', 'os', 'browser', 'is_active')

# -------------------------------
# IPActivity Admin
# -------------------------------
@admin.register(IPActivity)
class IPActivityAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'user', 'endpoint', 'method', 'request_count', 'failed_attempts', 'is_suspicious', 'last_seen')
    search_fields = ('ip_address', 'user__email', 'endpoint')
    list_filter = ('method', 'is_suspicious')

# -------------------------------
# BlacklistedIP Admin
# -------------------------------
@admin.register(BlacklistedIP)
class BlacklistedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'is_active', 'created_at')
    search_fields = ('ip_address', 'reason')
    list_filter = ('is_active',)
