#!/usr/bin/env python
"""Django のコマンドラインユーティリティ"""
import os
import sys


def main():
    """管理コマンドを実行する"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Django をインポートできませんでした。インストール済みであること、'
            'VIRTUAL_ENV が有効であることを確認してください。'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
