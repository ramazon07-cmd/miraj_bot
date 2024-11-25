from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import *


@admin.register(TelegramUserModel)
class ServiceModelAdmin(admin.ModelAdmin):
    list_filter = ['created_at']
    list_display = ['tg_id', 'username', 'first_name', 'last_name']
    search_fields = ['tg_id', 'username', 'first_name', 'last_name']


# @admin.register(ProductModel)
# class ServiceModelAdmin(admin.ModelAdmin):
#     list_filter = ['created']
#     list_display = ['title']
#     search_fields = ['title']


@admin.register(OrderModel)
class ServiceModelAdmin(admin.ModelAdmin):
    list_filter = ['created_at', 'order']
    list_display = ['id', 'number', 'product', 'price', 'order', 'created_at']
    search_fields = ['product', 'id']


@admin.register(CategoryModel)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('title', 'created')
    fieldsets = (
        (None, {
            'fields': ('title',)
        }),
    )

@admin.register(ProductModel)
class ProductAdmin(TranslatableAdmin):
    list_display = ('title', 'category', 'price', 'created')
    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'price', 'description', 'image')
        }),
    )

admin.site.register(KorzinaModel)
