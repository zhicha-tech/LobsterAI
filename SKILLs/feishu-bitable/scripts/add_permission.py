#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为飞书文档添加协作者权限脚本
用法: python add_permission.py --token "文档ID" --open-id "用户OpenID"
"""

import sys
import os
import argparse
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_feishu_credentials, get_tenant_access_token


def add_permission(app_token: str, open_id: str, notify: bool = True) -> dict:
    """
    为飞书文档添加用户协作者权限

    Args:
        app_token: 多维表格 ID (app_token)
        open_id: 用户的 Open ID
        notify: 是否通知用户

    Returns:
        操作结果字典
    """
    token = get_tenant_access_token()

    if not token:
        return {"success": False, "error": "获取访问令牌失败"}

    url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{app_token}/members/batch_create"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    params = {
        'type': 'bitable',
        'need_notification': notify
    }

    body = {
        "members": [
            {
                "member_type": "openid",
                "member_id": open_id,
                "perm": "full_access",
                "type": "user"
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=body,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 0:
            return {"success": True, "data": result.get('data', {})}
        else:
            return {
                "success": False,
                "error": f"错误码: {result.get('code')}, 错误信息: {result.get('msg')}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"网络请求失败: {e}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON 解析失败: {e}"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='为飞书多维表格添加协作者权限')
    parser.add_argument('--app_token', '-token', type=str, required=True, help='多维表格 ID')
    parser.add_argument('--open-id', '-o', type=str, help='用户 Open ID（不指定则使用配置文件中的 openUserId）')
    parser.add_argument('--no-notify', action='store_true', help='不通知用户')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    # 获取 open_id
    open_id = args.open_id
    if not open_id:
        _, _, open_id = get_feishu_credentials()
        if not open_id:
            print("❌ 未指定 open-id 且配置文件中没有 openUserId")
            sys.exit(1)

    result = add_permission(args.app_token, open_id, notify=not args.no_notify)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            print(f"✅ 权限添加成功!")
            members = result.get('data', {}).get('members', [])
            if members:
                for member in members:
                    print(f"   用户: {member.get('member_id')}")
                    print(f"   权限: {member.get('perm')}")
        else:
            print(f"❌ {result['error']}")
            sys.exit(1)
