from django.contrib import admin
from .models import *


class ItemRowInline (admin.TabularInline):
    model = ItemRow
    extra = 0

class ItemFileInline (admin.TabularInline):
    model = ItemFile
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    model = Item
    inlines = [ItemRowInline]

class ItemRowAdmin(admin.ModelAdmin):
    list_display = ('item','amount', 'is_income','is_outcome',)
    list_filter = ('item','is_income','is_outcome',)
    model = ItemRow
    inlines = [ItemFileInline]

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemRow, ItemRowAdmin)