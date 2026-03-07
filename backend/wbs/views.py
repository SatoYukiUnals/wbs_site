from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WBSItem
from .serializers import WBSItemSerializer


class WBSItemViewSet(viewsets.ModelViewSet):
    serializer_class = WBSItemSerializer

    def get_queryset(self):
        return WBSItem.objects.filter(parent=None).order_by('order', 'id')

    @action(detail=False, methods=['get'])
    def all(self, request):
        queryset = WBSItem.objects.all().order_by('order', 'id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
