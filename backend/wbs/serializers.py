from rest_framework import serializers
from .models import WBSItem


class WBSItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = WBSItem
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'assignee',
            'start_date', 'end_date', 'progress', 'parent',
            'order', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_children(self, obj):
        children = obj.children.all()
        return WBSItemSerializer(children, many=True).data
