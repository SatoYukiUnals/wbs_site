"""
テンプレート管理ビュー
"""
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Template
from .serializers import TemplateSerializer


class TemplateListCreateView(generics.ListCreateAPIView):
    """テンプレート一覧取得・作成エンドポイント"""

    serializer_class = TemplateSerializer

    def get_queryset(self):
        """テナント内テンプレート（自分作成 + 共有テンプレート）を返す"""
        tenant = self.request.user.tenant
        return Template.objects.filter(tenant=tenant).order_by('-created_at')


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """テンプレート取得・更新・削除エンドポイント"""

    serializer_class = TemplateSerializer

    def get_queryset(self):
        """テナント内テンプレートのみアクセス可能にする"""
        return Template.objects.filter(tenant=self.request.user.tenant)

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs['template_id'])
