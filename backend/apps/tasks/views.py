"""
タスク・レビュー管理ビュー
"""
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project

from .models import Review, ReviewComment, ReviewHistory, Task, TaskAssignee, TaskStatusHistory
from .serializers import (
    ReviewCommentSerializer,
    ReviewHistorySerializer,
    ReviewSerializer,
    TaskCreateSerializer,
    TaskOrderSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
)
from .utils import generate_wbs_no, recalculate_progress, regenerate_wbs_nos


def get_project_or_404(project_id, user):
    """プロジェクトをテナント検証付きで取得する。存在しない場合は None を返す。"""
    try:
        return Project.objects.get(
            id=project_id,
            tenant=user.tenant,
            deleted_at__isnull=True,
        )
    except Project.DoesNotExist:
        return None


class TaskListCreateView(generics.ListCreateAPIView):
    """タスク一覧取得・作成エンドポイント"""

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        """
        ルートタスク（parent_task=None）のみ返す。
        TaskSerializer で children を再帰的にシリアライズする。
        """
        project_id = self.kwargs['project_id']
        return Task.objects.filter(
            project__id=project_id,
            project__tenant=self.request.user.tenant,
            parent_task__isnull=True,
            deleted_at__isnull=True,
        ).order_by('order', 'created_at')

    def create(self, request, *args, **kwargs):
        """タスクを作成して depth・wbs_no を自動設定する"""
        project = get_project_or_404(self.kwargs['project_id'], request.user)
        if project is None:
            return Response({'detail': 'プロジェクトが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # depth を親タスクから計算する
        parent_task = data.get('parent_task')
        if parent_task is not None:
            # 深さ制限: 最大2階層（0/1/2）
            if parent_task.depth >= 2:
                return Response(
                    {'detail': 'タスクの深さは最大3階層（depth 0/1/2）までです。'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            depth = parent_task.depth + 1
        else:
            depth = 0

        task = Task.objects.create(
            project=project,
            depth=depth,
            wbs_no='',  # 後で生成する
            **data,
        )

        # wbs_no を生成して保存する
        task.wbs_no = generate_wbs_no(task)
        task.save(update_fields=['wbs_no'])

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskBulkCreateView(APIView):
    """タスク一括作成エンドポイント"""

    def post(self, request, project_id):
        """タスクを一括で作成する"""
        project = get_project_or_404(project_id, request.user)
        if project is None:
            return Response({'detail': 'プロジェクトが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        from django.db.models import Max

        tasks_data = request.data if isinstance(request.data, list) else request.data.get('tasks', [])
        created_tasks = []
        # 親ごとに次の order 値をキャッシュする（バッチ内で重複しないよう +1 ずつ増やす）
        next_order: dict = {}

        for task_data in tasks_data:
            serializer = TaskCreateSerializer(data=task_data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            parent_task = data.get('parent_task')
            depth = (parent_task.depth + 1) if parent_task else 0

            if parent_task and parent_task.depth >= 2:
                continue  # 深さ超過は無視する

            # 親ごとに既存最大 order+1 をベースに order を割り当てる
            parent_key = str(parent_task.id) if parent_task else '__root__'
            if parent_key not in next_order:
                existing_max = Task.objects.filter(
                    project=project,
                    parent_task=parent_task,
                    deleted_at__isnull=True,
                ).aggregate(v=Max('order'))['v'] or 0
                next_order[parent_key] = existing_max + 1
            data['order'] = next_order[parent_key]
            next_order[parent_key] += 1

            task = Task.objects.create(project=project, depth=depth, wbs_no='', **data)
            created_tasks.append(task)

        # 全タスクの wbs_no を再採番して整合させる
        regenerate_wbs_nos(project)

        # 再採番後の最新 wbs_no を返す
        created_ids = [t.id for t in created_tasks]
        refreshed = list(Task.objects.filter(id__in=created_ids).order_by('wbs_no'))
        return Response(
            TaskSerializer(refreshed, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """タスク取得・更新・削除エンドポイント"""

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(
            project__id=self.kwargs['project_id'],
            project__tenant=self.request.user.tenant,
            deleted_at__isnull=True,
        )

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs['task_id'])

    def update(self, request, *args, **kwargs):
        """タスク更新時にステータス変更履歴を記録して進捗率を再集計する"""
        task = self.get_object()
        old_status = task.status

        partial = kwargs.pop('partial', False)
        serializer = TaskUpdateSerializer(task, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ステータスが変わった場合は履歴を記録する
        new_status = serializer.instance.status
        if old_status != new_status:
            TaskStatusHistory.objects.create(
                task=task,
                status=new_status,
                changed_by=request.user,
            )

        # 進捗率を再集計する
        recalculate_progress(task.project)

        return Response(TaskSerializer(task).data)

    def destroy(self, request, *args, **kwargs):
        """論理削除（deleted_at を設定する）"""
        task = self.get_object()
        task.deleted_at = timezone.now()
        task.save(update_fields=['deleted_at'])

        # 子タスクも再帰的に論理削除する
        _soft_delete_children(task)

        # wbs_no を再採番する
        regenerate_wbs_nos(task.project)

        return Response(status=status.HTTP_204_NO_CONTENT)


def _soft_delete_children(task):
    """子タスクを再帰的に論理削除する"""
    children = Task.objects.filter(parent_task=task, deleted_at__isnull=True)
    now = timezone.now()
    for child in children:
        child.deleted_at = now
        child.save(update_fields=['deleted_at'])
        _soft_delete_children(child)


class TaskOrderView(APIView):
    """タスク並び順更新エンドポイント"""

    def patch(self, request, project_id, task_id):
        """タスクの order と parent_task を更新して wbs_no を再採番する"""
        try:
            task = Task.objects.get(
                id=task_id,
                project__id=project_id,
                project__tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Task.DoesNotExist:
            return Response({'detail': 'タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task.order = serializer.validated_data['order']

        # 親タスクの変更があれば depth も更新する
        if 'parent_task' in serializer.validated_data:
            new_parent_id = serializer.validated_data.get('parent_task')
            if new_parent_id:
                try:
                    new_parent = Task.objects.get(id=new_parent_id, project=task.project)
                    if new_parent.depth >= 2:
                        return Response(
                            {'detail': 'タスクの深さは最大3階層（depth 0/1/2）までです。'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    task.parent_task = new_parent
                    task.depth = new_parent.depth + 1
                except Task.DoesNotExist:
                    return Response({'detail': '親タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)
            else:
                task.parent_task = None
                task.depth = 0

        task.save()

        # プロジェクト全体の wbs_no を再採番する
        regenerate_wbs_nos(task.project)

        return Response(TaskSerializer(task).data)


class TaskAssigneeView(APIView):
    """タスク担当者追加・削除エンドポイント"""

    def post(self, request, project_id, task_id):
        """担当者を追加する"""
        try:
            task = Task.objects.get(
                id=task_id,
                project__id=project_id,
                project__tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Task.DoesNotExist:
            return Response({'detail': 'タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id が必要です。'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.accounts.models import User
        try:
            user = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({'detail': 'ユーザーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        assignee, created = TaskAssignee.objects.get_or_create(task=task, user=user)
        if not created:
            return Response({'detail': 'すでに担当者として登録されています。'}, status=status.HTTP_400_BAD_REQUEST)

        from .serializers import TaskAssigneeSerializer
        return Response(TaskAssigneeSerializer(assignee).data, status=status.HTTP_201_CREATED)

    def delete(self, request, project_id, task_id, user_id):
        """担当者を削除する"""
        try:
            assignee = TaskAssignee.objects.get(
                task__id=task_id,
                task__project__id=project_id,
                task__project__tenant=request.user.tenant,
                user__id=user_id,
            )
        except TaskAssignee.DoesNotExist:
            return Response({'detail': '担当者が見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        assignee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- レビュー管理 ----

class ReviewView(APIView):
    """レビュー取得・コメント追加エンドポイント"""

    def get_task(self, project_id, task_id, user):
        """タスクをテナント検証付きで取得する"""
        try:
            return Task.objects.get(
                id=task_id,
                project__id=project_id,
                project__tenant=user.tenant,
                deleted_at__isnull=True,
            )
        except Task.DoesNotExist:
            return None

    def get(self, request, project_id, task_id):
        """タスクのレビュー情報を返す"""
        task = self.get_task(project_id, task_id, request.user)
        if task is None:
            return Response({'detail': 'タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = task.review
        except Review.DoesNotExist:
            return Response({'detail': 'レビューが存在しません。'}, status=status.HTTP_404_NOT_FOUND)

        return Response(ReviewSerializer(review).data)

    def post(self, request, project_id, task_id, review_id):
        """レビューにコメントを追加する"""
        try:
            review = Review.objects.get(
                id=review_id,
                task__id=task_id,
                task__project__id=project_id,
                task__project__tenant=request.user.tenant,
            )
        except Review.DoesNotExist:
            return Response({'detail': 'レビューが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        body = request.data.get('body', '')
        if not body:
            return Response({'detail': 'コメント本文は必須です。'}, status=status.HTTP_400_BAD_REQUEST)

        comment = ReviewComment.objects.create(
            review=review,
            body=body,
            author=request.user,
        )
        # 操作履歴を記録する
        ReviewHistory.objects.create(
            review=review,
            task=review.task,
            action='commented',
            user=request.user,
        )
        return Response(ReviewCommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class ReviewApproveView(APIView):
    """レビュー承認エンドポイント"""

    def post(self, request, project_id, task_id):
        """レビューを承認してタスクステータスを更新する"""
        try:
            task = Task.objects.get(
                id=task_id,
                project__id=project_id,
                project__tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Task.DoesNotExist:
            return Response({'detail': 'タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = task.review
        except Review.DoesNotExist:
            return Response({'detail': 'レビューが存在しません。'}, status=status.HTTP_404_NOT_FOUND)

        if review.status != 'pending':
            return Response({'detail': 'このレビューはすでに完了しています。'}, status=status.HTTP_400_BAD_REQUEST)

        review.status = 'approved'
        review.reviewer = request.user
        review.save()

        # タスクステータスを Done に更新する
        task.status = 'Done'
        task.save(update_fields=['status'])

        # ステータス変更履歴を記録する
        TaskStatusHistory.objects.create(task=task, status='Done', changed_by=request.user)

        # 操作履歴を記録する
        ReviewHistory.objects.create(review=review, task=task, action='approved', user=request.user)

        # 進捗率を再集計する
        recalculate_progress(task.project)

        return Response(ReviewSerializer(review).data)


class ReviewRejectView(APIView):
    """レビュー差し戻しエンドポイント"""

    def post(self, request, project_id, task_id):
        """レビューを差し戻してタスクステータスを更新する"""
        try:
            task = Task.objects.get(
                id=task_id,
                project__id=project_id,
                project__tenant=request.user.tenant,
                deleted_at__isnull=True,
            )
        except Task.DoesNotExist:
            return Response({'detail': 'タスクが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = task.review
        except Review.DoesNotExist:
            return Response({'detail': 'レビューが存在しません。'}, status=status.HTTP_404_NOT_FOUND)

        if review.status != 'pending':
            return Response({'detail': 'このレビューはすでに完了しています。'}, status=status.HTTP_400_BAD_REQUEST)

        review.status = 'rejected'
        review.reviewer = request.user
        review.save()

        # タスクステータスを InProgress に戻す
        task.status = 'InProgress'
        task.save(update_fields=['status'])

        # ステータス変更履歴を記録する
        TaskStatusHistory.objects.create(task=task, status='InProgress', changed_by=request.user)

        # 操作履歴を記録する
        reason = request.data.get('reason', '')
        ReviewHistory.objects.create(review=review, task=task, action='rejected', user=request.user)

        if reason:
            ReviewComment.objects.create(review=review, body=reason, author=request.user)

        return Response(ReviewSerializer(review).data)


class ReviewHistoryView(generics.ListAPIView):
    """レビュー操作履歴一覧エンドポイント"""

    serializer_class = ReviewHistorySerializer

    def get_queryset(self):
        return ReviewHistory.objects.filter(
            task__id=self.kwargs['task_id'],
            task__project__id=self.kwargs['project_id'],
            task__project__tenant=self.request.user.tenant,
        )


class ProjectReviewListView(generics.ListAPIView):
    """プロジェクト内の全レビュー一覧エンドポイント"""

    serializer_class = ReviewSerializer

    def get_queryset(self):
        """プロジェクト配下の全タスクのレビューをまとめて返す"""
        return Review.objects.filter(
            task__project__id=self.kwargs['project_id'],
            task__project__tenant=self.request.user.tenant,
            task__deleted_at__isnull=True,
        ).select_related('task', 'reviewer').order_by('-created_at')


class ApplyTemplateView(APIView):
    """テンプレート適用エンドポイント（スタブ）"""

    def post(self, request, project_id, task_id):
        """タスクにテンプレートを適用する（未実装）"""
        return Response({'detail': 'テンプレート適用は現在未実装です。'})
