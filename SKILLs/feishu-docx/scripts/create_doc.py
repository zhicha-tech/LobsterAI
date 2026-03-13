#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建飞书文档脚本
用法: python create_doc.py --title "文档标题"
"""

import sys
import os
import argparse
import json

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_mcp_client import FeishuMCPClient
from config import get_feishu_credentials


def create_document(title: str) -> dict:
    """
    创建飞书文档

    Args:
        title: 文档标题

    Returns:
        包含 document_id 和 url 的字典
    """
    app_id, app_secret, _ = get_feishu_credentials()

    if not app_id or not app_secret:
        return {"success": False, "error": "未配置飞书凭证"}

    client = FeishuMCPClient(app_id=app_id, app_secret=app_secret)

    # 初始化
    if not client.initialize():
        return {"success": False, "error": "MCP 初始化失败"}

    # 调用创建文档工具
    result = client.call_tool(
        tool_name='create-doc',
        arguments={'title': title},
        allowed_tools=['create-doc']
    )

    if result:
        return {"success": True, "data": result}
    else:
        return {"success": False, "error": "创建文档失败"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='创建飞书文档')
    parser.add_argument('--title', '-t', type=str, required=True, help='文档标题')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    result = create_document(args.title)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            data = result['data']
            print(f"✅ 文档创建成功!")
            print(f"   Document ID: {data.get('document_id', data.get('docId', 'N/A'))}")
            print(f"   URL: {data.get('url', 'N/A')}")
        else:
            print(f"❌ {result['error']}")
            sys.exit(1)
