from django.contrib import admin
from .models import *


class ItemRowInline (admin.TabularInline):
    model = ItemRow
    extra = 0

class ItemFileInline (admin.TabularInline):
    model = ItemFile
    extra = 0

class ItemAccountInline (admin.TabularInline):
    model = ItemAccount
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    model = Item
    inlines = [ItemAccountInline]

class ItemAccountAdmin(admin.ModelAdmin):
    model = ItemAccount
    list_filter = ('item',)
    inlines = [ItemRowInline]

class ItemRowAdmin(admin.ModelAdmin):
    list_display = ('account','amount', 'is_income','is_outcome',)
    list_filter = ('account__item','account','is_income','is_outcome','month',)
    model = ItemRow
    inlines = [ItemFileInline]

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemRow, ItemRowAdmin)
admin.site.register(ItemAccount, ItemAccountAdmin)
admin.site.register(Month)
admin.site.register(RowMonthAmount)