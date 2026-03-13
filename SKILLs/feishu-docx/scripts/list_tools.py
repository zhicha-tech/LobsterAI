#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证飞书配置脚本
用法: python list_tools.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_mcp_client import FeishuMCPClient
from config import get_feishu_credentials, get_config_path


def verify_config() -> bool:
    """
    验证飞书配置是否正确

    Returns:
        配置是否有效
    """
    print(f"📋 配置文件路径: {get_config_path()}")

    app_id, app_secret, open_user_id = get_feishu_credentials()

    if not app_id or not app_secret:
        print("❌ 未找到有效配置")
        print("   请在配置文件中设置 channels.feishu.appId 和 channels.feishu.appSecret")
        return False

    print(f"✅ App ID: {app_id[:15]}...")
    print(f"✅ App Secret: {'*' * 15}")

    if open_user_id:
        print(f"✅ Open User ID: {open_user_id}")
    else:
        print("⚠️  未配置 openUserId，添加权限功能将不可用")

    # 测试 MCP 连接
    print("\n🔄 测试 MCP 连接...")

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    if not client.initialize():
        print("❌ MCP 初始化失败")
        return False

    print("✅ MCP 连接成功")

    # 列出可用工具
    print("\n📋 可用工具列表:")
    tools = client.list_tools([
        'create-doc', 'fetch-doc', 'update-doc', 'search-doc',
        'list-docs', 'get-comments', 'add-comments'
    ])

    if tools:
        return True
    else:
        print("⚠️  未获取到工具列表")
        return False


if __name__ == '__main__':
    success = verify_config()
    print("\n" + "="*60)
    if success:
        print("✅ 配置验证通过，所有功能可用")
    else:
        print("❌ 配置验证失败，请检查配置")
        sys.exit(1)
