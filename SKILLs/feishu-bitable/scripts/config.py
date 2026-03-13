#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
从用户目录的 .lawclaw.json 读取飞书配置
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict


def get_config_path() -> Path:
    """获取配置文件路径"""
    return Path.home() / ".lawclaw.json"


def load_config() -> Optional[Dict]:
    """
    加载配置文件
    返回飞书配置字典或 None
    """
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        feishu_config = config.get('channels', {}).get('feishu', {})
        if feishu_config.get('appId') and feishu_config.get('appSecret'):
            return feishu_config
        return None
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ 配置文件读取失败: {e}")
        return None


def get_feishu_credentials() -> tuple:
    """
    获取飞书凭证
    返回 (app_id, app_secret, open_user_id)
    """
    config = load_config()

    if config:
        app_id = config.get('appId')
        app_secret = config.get('appSecret')
        open_user_id = config.get('openUserId')
        return app_id, app_secret, open_user_id

    # 尝试从环境变量获取
    app_id = os.environ.get('FEISHU_APP_ID')
    app_secret = os.environ.get('FEISHU_APP_SECRET')
    open_user_id = os.environ.get('FEISHU_OPEN_USER_ID')

    return app_id, app_secret, open_user_id


def get_tenant_access_token() -> Optional[str]:
    """
    获取 tenant_access_token
    直接从飞书 API 获取
    """
    app_id, app_secret, _ = get_feishu_credentials()

    if not app_id or not app_secret:
        print("❌ 未配置飞书凭证，请先配置")
        return None

    import requests

    try:
        response = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            headers={'Content-Type': 'application/json; charset=utf-8'},
            json={
                "app_id": app_id,
                "app_secret": app_secret
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        if result.get('code') != 0:
            print(f"❌ 获取 token 失败: {result.get('msg')}")
            return None

        return result['tenant_access_token']

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return None


if __name__ == '__main__':
    # 测试配置
    print("📋 配置文件路径:", get_config_path())

    app_id, app_secret, open_user_id = get_feishu_credentials()
    if app_id:
        print(f"✅ App ID: {app_id[:10]}...")
        print(f"✅ App Secret: {'*' * 10}")
        if open_user_id:
            print(f"✅ Open User ID: {open_user_id}")
    else:
        print("❌ 未找到有效配置")

    # 测试获取 token
    token = get_tenant_access_token()
    if token:
        print(f"✅ Token: {token[:20]}...")
