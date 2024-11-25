from rest_framework import serializers
from .models import *

class TelegramRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUserModel
        fields = '__all__'


class CategoryModelSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = CategoryModel
        fields = ['id', 'title', 'created']

    def get_title(self, obj):
        request = self.context.get('request', None)
        lang = request.GET.get('lang', 'en') if request else 'en'
        return obj.safe_translation_getter('title', language_code=lang)


class ServiceModelSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'category', 'title', 'price', 'description', 'image', 'created']

    def get_title(self, obj):
        request = self.context.get('request', None)
        lang = request.GET.get('lang', 'en') if request else 'en'
        return obj.safe_translation_getter('title', language_code=lang)


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderModel
        fields = '__all__'


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUserModel
        fields = '__all__'


class KorzinaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = KorzinaModel
        fields = '__all__'
