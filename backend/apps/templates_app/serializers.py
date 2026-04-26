"""
テンプレート管理シリアライザー
"""
from rest_framework import serializers

from .models import Template


class TemplateSerializer(serializers.ModelSerializer):
    """テンプレートシリアライザー"""

    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Template
        fields = [
            'id', 'tenant', 'title', 'type', 'content',
            'is_shared', 'created_by', 'created_by_name', 'created_at',
        ]
        read_only_fields = ['id', 'tenant', 'created_by', 'created_at']

    def create(self, validated_data):
        """テンプレート作成時にテナント・作成者を自動設定する"""
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        validated_data['created_by'] = request.user
        return Template.objects.create(**validated_data)
