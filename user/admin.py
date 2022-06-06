from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *



class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'fio',
        'email',

    )
    ordering = ('id',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('fio',
                        'email',
                       'password1',
                       'password2',

                       ), }),)
    search_fields = ('id','email', 'fio', )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info',
         {'fields': (
             'fio',

         )}
         ),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups',)}),)

admin.site.register(User, UserAdmin)


