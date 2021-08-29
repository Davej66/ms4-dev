from django.contrib import admin
from .models import MyAccount, Skills, Roles


class UserAdmin(admin.ModelAdmin):
    list_display = ('email','first_name', 'last_name', 'package_name', 'profile_completed')
    search_fields = ('pk', 'email','first_name', 'last_name')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
admin.site.register(MyAccount, UserAdmin)
admin.site.register(Skills)
admin.site.register(Roles)