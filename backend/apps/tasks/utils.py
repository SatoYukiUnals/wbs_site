"""
タスクユーティリティ関数
wbs_no 生成・進捗率再集計などの共通ロジックを提供する
"""
from django.db.models import Avg


def generate_wbs_no(task):
    """
    タスクの wbs_no を生成する。
    深さ0（ルート）: プロジェクト内の並び順 "1", "2", ...
    深さ1（子）:    親の wbs_no + "." + 子の並び順 "1.1", "1.2", ...
    深さ2（孫）:    "1.1.1", "1.1.2", ...
    """
    from .models import Task

    if task.parent_task is None:
        # ルートタスクの場合: 同プロジェクト内での順位を計算する
        siblings = Task.objects.filter(
            project=task.project,
            parent_task__isnull=True,
            deleted_at__isnull=True,
        ).order_by('order', 'created_at')
        position = _get_position(siblings, task)
        return str(position)
    else:
        # 子タスクの場合: 親の wbs_no に子の順位を結合する
        parent = task.parent_task
        siblings = Task.objects.filter(
            parent_task=parent,
            deleted_at__isnull=True,
        ).order_by('order', 'created_at')
        position = _get_position(siblings, task)
        return f'{parent.wbs_no}.{position}'


def _get_position(siblings_qs, task):
    """兄弟タスクの中での 1 始まり順位を返す"""
    for idx, sibling in enumerate(siblings_qs, start=1):
        if str(sibling.id) == str(task.id):
            return idx
    # 見つからない場合は最後に配置する
    return siblings_qs.count()


def recalculate_progress(project):
    """
    プロジェクト進捗率を再集計してプロジェクトに保存する。
    - プロジェクト進捗率: 全タスク progress の平均
    - クォーター進捗率: クォーター内タスク progress の平均
    """
    from apps.projects.models import Quarter
    from .models import Task

    # プロジェクト全体の進捗率を再計算する
    avg_result = Task.objects.filter(
        project=project,
        deleted_at__isnull=True,
    ).aggregate(avg_progress=Avg('progress'))

    project.progress = round(avg_result['avg_progress'] or 0)
    project.save(update_fields=['progress'])

    # クォーターごとの進捗率を再計算する
    quarters = Quarter.objects.filter(project=project)
    for quarter in quarters:
        q_avg = Task.objects.filter(
            project=project,
            quarter=quarter,
            deleted_at__isnull=True,
        ).aggregate(avg_progress=Avg('progress'))
        quarter.progress = round(q_avg['avg_progress'] or 0)
        quarter.save(update_fields=['progress'])


def regenerate_wbs_nos(project):
    """
    プロジェクト内の全タスクの wbs_no を再生成する。
    タスクの並び順が変わったときに呼び出す。
    """
    from .models import Task

    def process_tasks(tasks, parent_wbs_prefix=''):
        """再帰的に wbs_no を付番する"""
        for idx, task in enumerate(tasks, start=1):
            if parent_wbs_prefix:
                task.wbs_no = f'{parent_wbs_prefix}.{idx}'
            else:
                task.wbs_no = str(idx)
            task.save(update_fields=['wbs_no'])

            # 子タスクを再帰的に処理する
            children = list(
                Task.objects.filter(
                    parent_task=task,
                    deleted_at__isnull=True,
                ).order_by('order', 'created_at')
            )
            if children:
                process_tasks(children, task.wbs_no)

    # ルートタスクから処理を開始する
    root_tasks = list(
        Task.objects.filter(
            project=project,
            parent_task__isnull=True,
            deleted_at__isnull=True,
        ).order_by('order', 'created_at')
    )
    process_tasks(root_tasks)
